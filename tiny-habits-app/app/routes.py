from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.models import User, Habit
from app.forms import RegistrationForm, LoginForm, HabitForm
from werkzeug.urls import url_parse
from datetime import datetime, date, timedelta

@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html', title='Home')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('dashboard') # or 'index' if dashboard is not ready
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    habits = current_user.habits.order_by(Habit.creation_date.desc()).all()
    return render_template('dashboard.html', title='Dashboard', habits=habits, today_date=date.today())

@app.route('/add_habit', methods=['GET', 'POST'])
@login_required
def add_habit():
    form = HabitForm()
    if form.validate_on_submit():
        habit = Habit(
            anchor_moment=form.anchor_moment.data,
            tiny_behavior=form.tiny_behavior.data,
            celebration=form.celebration.data,
            author=current_user  # or user_id=current_user.id
        )
        db.session.add(habit)
        db.session.commit()
        flash('New tiny habit added!')
        return redirect(url_for('dashboard'))
    return render_template('add_habit.html', title='Add New Habit', form=form)

@app.route('/complete_habit/<int:habit_id>', methods=['POST'])
@login_required
def complete_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    if habit.author != current_user:
        abort(403) # Forbidden

    today = date.today()

    if habit.last_completed_date is None or habit.last_completed_date.date() < today:
        # Check if the habit was completed yesterday to continue the streak
        if habit.last_completed_date and habit.last_completed_date.date() == today - timedelta(days=1):
            habit.streak += 1
        else:
            # If it wasn't completed yesterday or never completed, reset streak to 1
            habit.streak = 1

        habit.last_completed_date = datetime.utcnow()
        db.session.commit()
        flash(f"Awesome! You completed '{habit.tiny_behavior}'. Now, don't forget your celebration: '{habit.celebration}'!", 'success')
    else:
        flash(f"You've already completed '{habit.tiny_behavior}' today! Keep up the great work!", 'info')

    return redirect(url_for('dashboard'))
