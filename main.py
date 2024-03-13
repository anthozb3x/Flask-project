from flask import Flask, render_template, g
import sqlite3

app = Flask(__name__)


""" DATABASE """
DATABASE = 'database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # Cette ligne permet d'accéder aux colonnes par leur nom
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

@app.route("/")
def hello_world():
    return render_template('index.html') 

@app.route('/login')
def login():
    return 'login'

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
