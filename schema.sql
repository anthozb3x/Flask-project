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

-- Insert users with hashed passwords
INSERT INTO users (username, password) VALUES ('user1@gmail.fr', '0b14d501a594442a01c6859541bcb3e8164d183d32937b851835442f69d5c94e');
INSERT INTO users (username, password) VALUES ('user2@gmail.fr', '6cf615d5bcaac778352a8f1f3360d23f02f34ec182e259897fd6ce485d7870d4');

-- Insert lists created by both users
INSERT INTO lists (title, created_by) VALUES ('Liste de course', 1);
INSERT INTO lists (title, created_by) VALUES ('Liste choses a prendre pour vacances', 2);

-- Insert items into the lists
INSERT INTO items (list_id, name, quantity, added_by) VALUES (1, 'pomme', 5, 1);
INSERT INTO items (list_id, name, quantity, added_by) VALUES (1, 'bombom', 3, 1);
INSERT INTO items (list_id, name, quantity, added_by) VALUES (1, 'livre sur python', 1, 1);
INSERT INTO items (list_id, name, quantity, added_by) VALUES (2, 'pull', 2, 2);
INSERT INTO items (list_id, name, quantity, added_by) VALUES (2, 't-shirt', 3, 2);

-- Insert invitations between the users
INSERT INTO invitations (list_id, user_id, status) VALUES (1, 2, 'pending');
INSERT INTO invitations (list_id, user_id, status) VALUES (2, 1, 'accepted');
