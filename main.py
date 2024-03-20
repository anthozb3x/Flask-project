from flask import Flask, render_template, g, request, redirect, url_for, flash, session,jsonify
from pathlib import Path
import sqlite3
import hashlib
from functools import wraps

app = Flask(__name__)
app.secret_key = 'sdkfjslkfjlrjaqriognioqzenfqrf:!zqjllskerfjdkjmoqrgsjerhkghqlzieMfehy'


"""DATABASE"""
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

def query(sql, args=(), one=False):
    db = get_db()
    cur = db.execute(sql, args)
    rv = cur.fetchall()
    db.commit() 
    return (rv[0] if rv else None) if one else rv

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vous devez être connecté pour accéder à cette page.')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


"""page route"""
@app.route("/")
@login_required
def home():
    user_id = session.get('user_id')
    private_lists = query('''
        SELECT * FROM lists
        WHERE created_by = ? AND NOT EXISTS (
            SELECT 1 FROM invitations WHERE list_id = lists.id
        )
    ''', (user_id,))
    
    shared_lists = query('''
        SELECT DISTINCT lists.* FROM lists
        LEFT JOIN invitations ON lists.id = invitations.list_id
        WHERE lists.created_by = ? OR invitations.user_id = ?
    ''', (user_id, user_id))
    
    return render_template('index.html', private_lists=private_lists, shared_lists=shared_lists)


"""CRUD LIST"""
@app.route("/edit_list", methods=['POST'])
@login_required
def edit_list():
    list_id = request.form.get('list_id')
    new_title = request.form.get('title')
    user_id = session.get('user_id')

    # Vérifie si l'utilisateur est le créateur ou un utilisateur invité autorisé
    list_info = query('''SELECT lists.id FROM lists
                          LEFT JOIN invitations ON lists.id = invitations.list_id
                          WHERE lists.id = ? AND 
                          (lists.created_by = ? OR (invitations.user_id = ? AND invitations.status = 'accepted'))''',
                      [list_id, user_id, user_id], one=True)
    
    if list_info:
        # Si l'utilisateur a le droit de modifier la liste
        query('UPDATE lists SET title = ? WHERE id = ?', [new_title, list_id])
        flash('Liste modifiée avec succès.')
    else:
        flash('Vous n\'avez pas les droits pour modifier cette liste.')

    return redirect(url_for('home'))

@app.route("/delete_list", methods=['POST'])
@login_required
def delete_list():
    list_id, user_id = request.form['list_id'], session.get('user_id')
    query('DELETE FROM lists WHERE id = ? AND created_by = ?', (list_id, user_id))
    flash('Liste supprimée avec succès.')
    return redirect(url_for('home'))

@app.route("/get_list_items/<int:list_id>")
def get_list_items(list_id):
    items = query("SELECT * FROM items WHERE list_id = ?", (list_id,))
    return jsonify([dict(item) for item in items])
"""Sytem d'auth"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username, password = request.form['email'], hashlib.sha256(request.form['password'].encode()).hexdigest()
        user = query('SELECT * FROM users WHERE username = ? AND password = ?', (username, password), one=True)
        if user:
            session['user_id'] = user['id']
            flash('Vous êtes connecté avec succès !')
            return redirect(url_for('home'))
        else:
            flash('Adresse email ou mot de passe incorrect.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username, password = request.form['email'], hashlib.sha256(request.form['password'].encode()).hexdigest()
        try:
            query('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            flash('Inscription réussie. Vous pouvez maintenant vous connecter.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Erreur : cet utilisateur existe déjà.')
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None) 
    flash('Vous avez été déconnecté.')
    return redirect(url_for('home'))



if __name__ == "__main__":
    bddPath = Path(DATABASE)
    if not bddPath.exists():
        init_db()
    app.run(debug=True)
