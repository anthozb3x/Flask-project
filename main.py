from flask import Flask, render_template, g, request, redirect, url_for, flash, session
from pathlib import Path
import sqlite3
import hashlib
from functools import wraps

app = Flask(__name__)
# app.secret_key = 'votre_clé_secrète_ici'

DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vous devez être connecté pour accéder à cette page.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
@login_required
def hello_world():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['email']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest() 

        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()

        if user:
            session['user_id'] = user['id']  # Stockage de l'ID utilisateur dans la session
            flash('Vous êtes connecté avec succès !')
            return redirect(url_for('hello_world'))
        else:
            flash('Adresse email ou mot de passe incorrect.')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None) 
    flash('Vous avez été déconnecté.')
    return redirect(url_for('hello_world'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['email']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()  # Hachage du mot de passe

        db = get_db()
        try:
            db.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            db.commit()
            flash('Inscription réussie. Vous pouvez maintenant vous connecter.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Erreur : cet utilisateur existe déjà.')
            return redirect(url_for('register'))

    return render_template('register.html')



if __name__ == "__main__":
    bddPath = Path(DATABASE)
    if not bddPath.exists():
        init_db()
    app.run(debug=True)
