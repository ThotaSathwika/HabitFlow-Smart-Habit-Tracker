import os
from datetime import datetime, timedelta, date
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, current_user, logout_user, login_required
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'habitflow_super_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///habitflow.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# Models
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    habits = db.relationship('Habit', backref='author', lazy=True)
    journals = db.relationship('JournalEntry', backref='author', lazy=True)
    achievements = db.relationship('Achievement', backref='user', lazy=True)

class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    logs = db.relationship('HabitLog', backref='habit', lazy=True, cascade="all, delete-orphan")

class HabitLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habit.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    completed = db.Column(db.Boolean, default=False)

class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    mood = db.Column(db.String(20), nullable=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    unlocked_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user, remember=request.form.get('remember'))
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/habits', methods=['GET', 'POST'])
@login_required
def habits():
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        if name and category:
            habit = Habit(name=name, category=category, author=current_user)
            db.session.add(habit)
            db.session.commit()
            flash('Habit added!', 'success')
        return redirect(url_for('habits'))
    
    user_habits = Habit.query.filter_by(author=current_user).all()
    today = date.today()
    habit_data = []
    
    for h in user_habits:
        log = HabitLog.query.filter_by(habit_id=h.id, date=today).first()
        completed = log.completed if log else False
        habit_data.append({'habit': h, 'completed': completed})
        
    return render_template('habits.html', habits=habit_data)

@app.route('/api/habits/<int:habit_id>/toggle', methods=['POST'])
@login_required
def toggle_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    if habit.author != current_user:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    action_date_str = data.get('date')
    if action_date_str:
        action_date = datetime.strptime(action_date_str, '%Y-%m-%d').date()
    else:
        action_date = date.today()
        
    log = HabitLog.query.filter_by(habit_id=habit.id, date=action_date).first()
    
    if log:
        log.completed = not log.completed
    else:
        log = HabitLog(habit_id=habit.id, date=action_date, completed=True)
        db.session.add(log)
        
    db.session.commit()
    
    return jsonify({'success': True, 'completed': log.completed, 'date': str(action_date)})

@app.route('/analytics')
@login_required
def analytics():
    return render_template('analytics.html')

@app.route('/api/chart_data')
@login_required
def chart_data():
    # Generate dummy chart data for now, or calculate based on HabitLog
    # In a real app, you'd calculate weekly progress based on actual logs
    return jsonify({
        'weekly_progress': [3, 4, 5, 2, 6, 4, 5],
        'monthly_consistency': {'completed': 20, 'missed': 10}
    })

@app.route('/journal')
@login_required
def journal():
    return render_template('journal.html')

@app.route('/achievements')
@login_required
def achievements():
    return render_template('achievements.html')

@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')

def seed_data():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email='test@example.com').first():
            hashed_password = bcrypt.generate_password_hash('password').decode('utf-8')
            user = User(username='TestUser', email='test@example.com', password=hashed_password)
            db.session.add(user)
            db.session.commit()
            
            h1 = Habit(name='Morning Workout', category='Fitness', author=user)
            h2 = Habit(name='Read 20 Minutes', category='Reading', author=user)
            h3 = Habit(name='Meditate', category='Meditation', author=user)
            db.session.add_all([h1, h2, h3])
            db.session.commit()
            
            # Seed some past logs
            today = date.today()
            for i in range(7):
                log_date = today - timedelta(days=i)
                db.session.add(HabitLog(habit_id=h1.id, date=log_date, completed=True if i % 2 == 0 else False))
                db.session.add(HabitLog(habit_id=h2.id, date=log_date, completed=True))
            db.session.commit()

if __name__ == '__main__':
    seed_data()
    app.run(debug=True, port=5001)
