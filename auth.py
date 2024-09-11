import functools

from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app)
from werkzeug.security import check_password_hash, generate_password_hash
from Countle.db import get_db, init_db
from gensim.models import KeyedVectors
import random

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


def calculate_similarity(word, country, model):
    try:
        similarity = model.similarity(word, country)
        return similarity
    except KeyError as e:
        return None  # Return None if the word or country is not in the model's vocabulary

@bp.route('/countle', methods=('GET', 'POST'))
def countle():
    db = get_db()
    result = None

    model = current_app.config['WORD2VEC_MODEL']

    target_word_row = db.execute('SELECT word FROM target_word LIMIT 1').fetchone()
    target_word = target_word_row['word'] if target_word_row else None 

    if request.method == 'POST' and 'word_butt' in request.form:

        db.execute("DELETE FROM target_word")

        countries = [
            "United States", "Canada", "Mexico", "Germany", "France",
            "Spain", "Italy", "United Kingdom", "Brazil", "India",
            "China", "Japan", "Russia", "Australia", "South Africa"
        ]
        
        word = random.choice(countries)
        db.execute("INSERT INTO target_word (word) VALUES (?)", (word,))
        db.commit()

        target_word_row = db.execute('SELECT word FROM target_word LIMIT 1').fetchone()
        target_word = target_word_row['word'] if target_word_row else None
        result = f"New word generated: {target_word}"

        guess = request.form['guess']

    elif request.method == 'POST':
        guess = request.form['guess']
        if guess.strip():
            if 'guess_butt' in request.form:
                if guess == target_word:
                    result = "correct"
                elif guess != target_word:
                    result = "incorrect"

            elif 'compare_butt' in request.form:
                score = calculate_similarity(guess, target_word, model)
                result = f"similarity = {score}"
    
    return render_template('countle.html', result=result)

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