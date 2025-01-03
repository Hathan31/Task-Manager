CREATE DATABASE taskManager;
USE taskManager;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE
);

CREATE TABLE tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255),
    due_date DATE,
    priority ENUM('Normal', 'Medium', 'High'),
    comments TEXT,
    status ENUM('Pending', 'In Progress', 'Completed'),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

DROP DATABASE taskManager;