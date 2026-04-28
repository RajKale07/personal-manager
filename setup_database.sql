-- Create database
CREATE DATABASE IF NOT EXISTS personal_manager;
USE personal_manager;

-- Create users table
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_date DATE NOT NULL
);

-- Create documents table
CREATE TABLE documents (
    document_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    document_name VARCHAR(100) NOT NULL,
    authority VARCHAR(100),
    issue_date DATE,
    expiry_date DATE,
    importance VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Create deadlines table
CREATE TABLE deadlines (
    deadline_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    due_date DATE NOT NULL,
    status VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Create goals table
CREATE TABLE goals (
    goal_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    goal_name VARCHAR(100) NOT NULL,
    start_date DATE,
    target_date DATE,
    progress INT DEFAULT 0,
    status VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Create contacts table
CREATE TABLE contacts (
    contact_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    contact_name VARCHAR(100) NOT NULL,
    relationship VARCHAR(50),
    phone VARCHAR(20),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Create tasks table
CREATE TABLE tasks (
    task_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    document_id INT NOT NULL,
    task_type VARCHAR(50) DEFAULT 'Renew',
    status VARCHAR(20) DEFAULT 'Pending',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (document_id) REFERENCES documents(document_id) ON DELETE CASCADE
);

-- Create view for expiring documents (within 30 days)
CREATE VIEW expiring_documents AS
SELECT * FROM documents
WHERE expiry_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY);

-- Create stored procedure for upcoming deadlines (within 7 days)
DELIMITER //
CREATE PROCEDURE get_upcoming_deadlines()
BEGIN
    SELECT * FROM deadlines
    WHERE due_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 7 DAY)
    ORDER BY due_date;
END //
DELIMITER ;

-- Insert sample data
INSERT INTO users (name, email, password, created_date) VALUES
('John Doe', 'john@example.com', 'password123', '2024-01-01'),
('Jane Smith', 'jane@example.com', 'password456', '2024-01-15');

INSERT INTO documents (user_id, document_name, authority, issue_date, expiry_date, importance) VALUES
(1, 'Passport', 'Government', '2020-01-01', '2030-01-01', 'High'),
(1, 'Driver License', 'DMV', '2022-06-15', '2026-06-15', 'High'),
(2, 'Insurance Policy', 'Insurance Co', '2024-01-01', DATE_ADD(CURDATE(), INTERVAL 15 DAY), 'Medium');

INSERT INTO deadlines (user_id, title, description, due_date, status) VALUES
(1, 'Project Submission', 'Submit final project report', DATE_ADD(CURDATE(), INTERVAL 5 DAY), 'Pending'),
(1, 'Tax Filing', 'File annual tax returns', DATE_ADD(CURDATE(), INTERVAL 3 DAY), 'Pending'),
(2, 'Meeting Preparation', 'Prepare presentation slides', DATE_ADD(CURDATE(), INTERVAL 2 DAY), 'In Progress');

INSERT INTO goals (user_id, goal_name, start_date, target_date, progress, status) VALUES
(1, 'Learn Python', '2024-01-01', '2024-06-30', 60, 'In Progress'),
(1, 'Complete DBMS Project', '2024-02-01', '2024-03-15', 80, 'In Progress'),
(2, 'Fitness Goal', '2024-01-01', '2024-12-31', 30, 'Active');

INSERT INTO contacts (user_id, contact_name, relationship, phone) VALUES
(1, 'Alice Johnson', 'Friend', '555-0101'),
(1, 'Bob Williams', 'Colleague', '555-0102'),
(2, 'Charlie Brown', 'Family', '555-0103');

SELECT 'Database setup completed successfully!' AS Message;
