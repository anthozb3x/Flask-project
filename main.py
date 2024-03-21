from flask import (
    Flask,
    render_template,
    g,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
)
from pathlib import Path
import sqlite3
import hashlib
from functools import wraps

app = Flask(__name__)
app.secret_key = "sdkfjslkfjlrjaqriognioqzenfqrf:!zqjllskerfjdkjmoqrgsjerhkghqlzieMfehy"


"""DATABASE"""
DATABASE = "database.db"


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource("schema.sql", mode="r") as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
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
        if "user_id" not in session:
            flash("Vous devez être connecté pour accéder à cette page.")
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


"""page route"""


def get_private_lists(user_id):
    private_lists_query = """
    SELECT lists.id, lists.title
    FROM lists
   
    WHERE lists.created_by = ? AND NOT EXISTS (
        SELECT * FROM invitations WHERE list_id = lists.id
    )
    ORDER BY lists.id;
    """
    return query(private_lists_query, (user_id,))


def get_shared_lists(user_id):
    shared_lists_query = """
    SELECT lists.id, lists.title
    FROM lists
    WHERE lists.created_by = ? AND EXISTS (
        SELECT 1 FROM invitations WHERE list_id = lists.id
    ) OR lists.id IN (
        SELECT list_id FROM invitations WHERE user_id = ? AND status = 'accepted'
    )
    ORDER BY lists.id;
    """
    return query(shared_lists_query, (user_id, user_id))


@app.route("/")
@login_required
def home():
    user_id = session.get("user_id")
    private_lists = get_private_lists(user_id)
    shared_lists = get_shared_lists(user_id)
    print(len(shared_lists))
    # Traitement des données pour les passer au template...
    return render_template(
        "index.html", private_lists=private_lists, shared_lists=shared_lists
    )


"""CRUD LIST"""


@app.route("/create_list", methods=["GET", "POST"])
@login_required
def create_list():
    if request.method == "POST":
        # Récupérer le titre de la liste à partir du formulaire
        title = request.form.get("title")
        user_id = session.get("user_id")

        if title:
            # Insérer la nouvelle liste dans la base de données
            query(
                "INSERT INTO lists (title, created_by) VALUES (?, ?)", (title, user_id)
            )
            flash("Nouvelle liste créée avec succès.")
            return redirect(url_for("home"))
        else:
            flash("Le titre de la liste ne peut pas être vide.")

    # Si la méthode est GET ou si le titre est vide, afficher le formulaire de création
    return render_template("create_list.html")


@app.route("/edit_list", methods=["POST"])
@login_required
def edit_list():
    list_id = request.form.get("list_id")
    new_title = request.form.get("title")
    user_id = session.get("user_id")

    # Vérifie si l'utilisateur est le créateur ou un utilisateur invité autorisé
    list_info = query(
        """SELECT lists.id FROM lists
                          LEFT JOIN invitations ON lists.id = invitations.list_id
                          WHERE lists.id = ? AND 
                          (lists.created_by = ? OR (invitations.user_id = ? AND invitations.status = 'accepted'))""",
        [list_id, user_id, user_id],
        one=True,
    )

    if list_info:
        # Mise à jour du titre de la liste
        query("UPDATE lists SET title = ? WHERE id = ?", [new_title, list_id])

        # Mise à jour des éléments existants
        for key, value in request.form.items():
            if key.startswith("item_name_"):
                item_id = key.split("_")[-1]
                item_name = value
                item_quantity = request.form.get(f"item_quantity_{item_id}")

                # Mettre à jour chaque élément existant
                query(
                    """UPDATE items SET name = ?, quantity = ? 
                         WHERE id = ? AND list_id = ?""",
                    [item_name, item_quantity, item_id, list_id],
                )

        # Ajout de nouveaux éléments
        for key, value in request.form.items():
            if key.startswith("new_item_name_"):
                new_item_name = value
                new_item_index = key.split("_")[-1]
                new_item_quantity = request.form.get(
                    f"new_item_quantity_{new_item_index}"
                )

                # Insérer le nouvel élément dans la base de données
                query(
                    """INSERT INTO items (list_id, name, quantity, added_by) 
                         VALUES (?, ?, ?, ?)""",
                    [list_id, new_item_name, new_item_quantity, user_id],
                )

        flash("Liste modifiée avec succès.")
    else:
        flash("Vous n'avez pas les droits pour modifier cette liste.")

    return redirect(url_for("home"))


@app.route("/delete_list", methods=["POST"])
@login_required
def delete_list():
    list_id, user_id = request.form["list_id"], session.get("user_id")
    query("DELETE FROM lists WHERE id = ? AND created_by = ?", (list_id, user_id))
    flash("Liste supprimée avec succès.")
    return redirect(url_for("home"))


@app.route("/get_list_items/<int:list_id>")
def get_list_items(list_id):
    items = query("SELECT * FROM items WHERE list_id = ?", (list_id,))
    return jsonify([dict(item) for item in items])


"""Sytem d'auth"""


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username, password = (
            request.form["email"],
            hashlib.sha256(request.form["password"].encode()).hexdigest(),
        )
        user = query(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password),
            one=True,
        )
        if user:
            session["user_id"] = user["id"]
            flash("Vous êtes connecté avec succès !")
            return redirect(url_for("home"))
        else:
            flash("Adresse email ou mot de passe incorrect.")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username, password = (
            request.form["email"],
            hashlib.sha256(request.form["password"].encode()).hexdigest(),
        )
        try:
            query(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password),
            )
            flash("Inscription réussie. Vous pouvez maintenant vous connecter.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Erreur : cet utilisateur existe déjà.")
    return render_template("register.html")


@app.route("/get_users")
@login_required
def get_users():
    current_user_id = session.get("user_id")
    users_query = "SELECT id, username FROM users WHERE id != ?"
    users = query(users_query, [current_user_id])
    return jsonify([{"id": user["id"], "username": user["username"]} for user in users])


@app.route("/share_list", methods=["POST"])
@login_required
def share_list():
    list_id = request.form.get("list_id")
    user_to_share_with_id = request.form.get("user_to_share")
    current_user_id = session.get(
        "user_id"
    )  # Assurez-vous d'avoir l'ID de l'utilisateur actuellement connecté.

    # Vérification : l'utilisateur actuel est-il le propriétaire de la liste ?
    list = query(
        """SELECT * FROM lists WHERE id = ? AND created_by = ?""",
        [list_id, current_user_id],
        one=True,
    )
    if list is None:
        flash("Vous n'avez pas l'autorisation de partager cette liste.", "error")
        return redirect(url_for("home"))

    # Vérifier si l'invitation existe déjà
    invitation = query(
        """SELECT * FROM invitations WHERE list_id = ? AND user_id = ?""",
        [list_id, user_to_share_with_id],
        one=True,
    )
    if invitation:
        flash("Cette liste a déjà été partagée avec l'utilisateur.", "info")
    else:
        # Partager la liste en créant une nouvelle invitation
        query(
            """INSERT INTO invitations (list_id, user_id, status) VALUES (?, ?, ?)""",
            [list_id, user_to_share_with_id, "pending"],
        )
        flash("Liste partagée avec succès.", "success")

    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Vous avez été déconnecté.")
    return redirect(url_for("home"))


"""INVITATION"""


@app.route("/invitations")
@login_required
def invitations():
    user_id = session.get("user_id")
    invitations_query = """
    SELECT invitations.id, lists.title, users.username as inviter, invitations.status
    FROM invitations
    JOIN lists ON lists.id = invitations.list_id
    JOIN users ON users.id = lists.created_by
    WHERE invitations.user_id = ? AND invitations.status = 'pending'
    """
    invitations = query(invitations_query, [user_id])
    return render_template("invitations.html", invitations=invitations)


@app.route("/accept_invitation/<int:invitation_id>")
@login_required
def accept_invitation(invitation_id):
    query(
        """UPDATE invitations SET status = 'accepted' WHERE id = ?""", [invitation_id]
    )
    flash("Invitation acceptée.")
    return redirect(url_for("invitations"))


@app.route("/decline_invitation/<int:invitation_id>")
@login_required
def decline_invitation(invitation_id):
    query(
        """UPDATE invitations SET status = 'declined' WHERE id = ?""", [invitation_id]
    )
    flash("Invitation refusée.")
    return redirect(url_for("invitations"))


if __name__ == "__main__":
    bddPath = Path(DATABASE)
    if not bddPath.exists():
        init_db()
    app.run(debug=True)
