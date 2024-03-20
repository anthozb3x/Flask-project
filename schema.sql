DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER PRIMARY KEY ,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
);

DROP TABLE IF EXISTS lists;
CREATE TABLE lists (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    created_by INTEGER NOT NULL,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

DROP TABLE IF EXISTS items;
CREATE TABLE items (
    id INTEGER PRIMARY KEY,
    list_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    added_by INTEGER NOT NULL,
    FOREIGN KEY (list_id) REFERENCES lists(id),
    FOREIGN KEY (added_by) REFERENCES users(id)
);

DROP TABLE IF EXISTS invitations;
CREATE TABLE invitations (
    id INTEGER PRIMARY KEY,
    list_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (list_id) REFERENCES lists(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Insertion de données fictives
-- Utilisateurs
INSERT INTO users (username, password) VALUES ('user1@gmail.fr', '0b14d501a594442a01c6859541bcb3e8164d183d32937b851835442f69d5c94e');



-- Listes
-- INSERT INTO lists (title, created_by) VALUES ('Liste de courses', 1);
-- INSERT INTO lists (title, created_by) VALUES ('Liste de tâches', 2);

-- Items
-- INSERT INTO items (list_id, name, quantity, added_by) VALUES (1, 'Pommes', 5, 1);
-- INSERT INTO items (list_id, name, quantity, added_by) VALUES (1, 'Bananes', 3, 2);
-- INSERT INTO items (list_id, name, quantity, added_by) VALUES (2, 'Nettoyer la maison', 1, 2);

-- Invitations
-- INSERT INTO invitations (list_id, user_id, status) VALUES (1, 2, 'pending');
-- INSERT INTO invitations (list_id, user_id, status) VALUES (2, 1, 'accepted');
