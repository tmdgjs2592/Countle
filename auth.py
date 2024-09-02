import functools

from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from Countle.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))

def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'

        if error is None:
            try:
                db.execute("INSERT INTO user (username, password) VALUES (?, ?)", (username, generate_password_hash(password)),)
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is alreayd registered."
            else:
                return redirect(url_for("auth.login"))
            
        flash(error) # the error is shown to the user
    return render_template('register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))
        
        flash (error)
    return render_template('login.html')


def calculate_similarity(guess, target_word):
    # Implement your similarity calculation logic here
    # For now, return a stub value
    return 0.0

@bp.route('/countle', methods=('GET', 'POST'))
def countle():
    return render_template('countle.html')
'''
@bp.route('/countle', methods=('GET', 'POST'))
def countle():
    db = get_db()
    error = None

    # Fetch the current target word
    target_word = db.execute('SELECT word FROM target_word LIMIT 1').fetchone()

    if not target_word:
        # Set a default target word if none is present
        target_word = 'sushi'
        db.execute('INSERT INTO target_word (word, date) VALUES (?, CURRENT_DATE)', (target_word,))
        db.commit()

    if request.method == 'POST':
        # Get user input
        username = request.form['username']
        guess = request.form['guess']

        if not username or not guess:
            error = 'Username and guess are required.'
        else:
            # Calculate similarity (stub for actual calculation)
            similarity_score = calculate_similarity(guess, target_word['word'])

            # Store the user guess
            db.execute(
                'INSERT INTO user_guess (username, guess, similarity_score) VALUES (?, ?, ?)',
                (username, guess, similarity_score)
            )
            db.commit()

            flash(f'Your guess: {guess}, Similarity score: {similarity_score}')
'''

@bp.before_app_request
def load_logged_in_user():

    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrapped_view