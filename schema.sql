DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

DROP TABLE IF EXISTS lists;
CREATE TABLE lists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    created_by INTEGER NOT NULL,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

DROP TABLE IF EXISTS items;
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    list_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    added_by INTEGER NOT NULL,
    FOREIGN KEY (list_id) REFERENCES lists(id),
    FOREIGN KEY (added_by) REFERENCES users(id)
);

DROP TABLE IF EXISTS invitations;
CREATE TABLE invitations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    list_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (list_id) REFERENCES lists(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Insertion de données fictives
-- Utilisateurs
INSERT INTO users (username, password) VALUES ('user1@maliste.fr', 'password1');
INSERT INTO users (username, password) VALUES ('user2@maliste.fr', 'password2');

-- Listes
INSERT INTO lists (title, created_by) VALUES ('Liste de courses', 1);
INSERT INTO lists (title, created_by) VALUES ('Liste de tâches', 2);

-- Items
INSERT INTO items (list_id, name, quantity, added_by) VALUES (1, 'Pommes', 5, 1);
INSERT INTO items (list_id, name, quantity, added_by) VALUES (1, 'Bananes', 3, 2);
INSERT INTO items (list_id, name, quantity, added_by) VALUES (2, 'Nettoyer la maison', 1, 2);

-- Invitations
INSERT INTO invitations (list_id, user_id, status) VALUES (1, 2, 'pending');
INSERT INTO invitations (list_id, user_id, status) VALUES (2, 1, 'accepted');
