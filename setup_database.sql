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

-- Create issue guide tables
CREATE TABLE issue_guide (
    guide_id INT PRIMARY KEY AUTO_INCREMENT,
    document_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE issue_guide_steps (
    step_id INT PRIMARY KEY AUTO_INCREMENT,
    guide_id INT NOT NULL,
    step_order INT NOT NULL,
    step_text VARCHAR(255) NOT NULL,
    FOREIGN KEY (guide_id) REFERENCES issue_guide(guide_id) ON DELETE CASCADE
);

CREATE TABLE issue_guide_required (
    req_id INT PRIMARY KEY AUTO_INCREMENT,
    guide_id INT NOT NULL,
    required_document VARCHAR(100) NOT NULL,
    FOREIGN KEY (guide_id) REFERENCES issue_guide(guide_id) ON DELETE CASCADE
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

-- Seed issue guide
INSERT INTO issue_guide (document_name) VALUES
('Passport'), ('Driving License'), ('Aadhaar Card'), ('PAN Card'),
('Voter ID'), ('Vehicle RC'), ('Insurance Policy'), ('Birth Certificate');

INSERT INTO issue_guide_steps (guide_id, step_order, step_text) VALUES
(1,1,'Fill Form-1 online at passportindia.gov.in'),
(1,2,'Book appointment at nearest Passport Seva Kendra'),
(1,3,'Visit PSK with original documents on appointment date'),
(1,4,'Biometric data and photo will be captured'),
(1,5,'Police verification will be conducted'),
(1,6,'Passport delivered to your address within 7-14 days'),
(2,1,'Apply for Learner''s License at sarathi.parivahan.gov.in'),
(2,2,'Pass the online theory test'),
(2,3,'Wait 30 days after Learner''s License'),
(2,4,'Book driving test slot at RTO'),
(2,5,'Appear for practical driving test at RTO'),
(2,6,'License issued if test passed'),
(3,1,'Visit nearest Aadhaar Enrollment Centre'),
(3,2,'Fill enrollment form'),
(3,3,'Submit biometric data (fingerprints + iris scan)'),
(3,4,'Get acknowledgement slip with enrollment ID'),
(3,5,'Download e-Aadhaar from uidai.gov.in after 90 days'),
(4,1,'Apply online at tin-nsdl.com or utiitsl.com'),
(4,2,'Fill Form 49A with personal details'),
(4,3,'Upload photo, signature and supporting documents'),
(4,4,'Pay application fee online'),
(4,5,'PAN card delivered within 15 working days'),
(5,1,'Apply online at voters.eci.gov.in'),
(5,2,'Fill Form 6 for new registration'),
(5,3,'Upload required documents'),
(5,4,'BLO will verify your details at your address'),
(5,5,'Voter ID card issued after verification'),
(6,1,'Visit RTO with vehicle and documents'),
(6,2,'Fill Form 20 for registration'),
(6,3,'Vehicle inspection by RTO officer'),
(6,4,'Pay registration fee'),
(6,5,'RC issued within 7 working days'),
(7,1,'Compare plans on insurance aggregator websites'),
(7,2,'Choose plan based on coverage and premium'),
(7,3,'Fill proposal form with personal and health details'),
(7,4,'Pay premium online'),
(7,5,'Policy document sent to registered email'),
(8,1,'Apply at Municipal Corporation / Gram Panchayat office'),
(8,2,'Fill birth registration form'),
(8,3,'Submit hospital discharge summary'),
(8,4,'Certificate issued within 7 days of application');

INSERT INTO issue_guide_required (guide_id, required_document) VALUES
(1,'Aadhaar Card'),(1,'Birth Certificate'),(1,'10th Marksheet'),(1,'Address Proof'),
(2,'Aadhaar Card'),(2,'Address Proof'),(2,'Age Proof'),(2,'Passport Photo'),
(3,'Birth Certificate'),(3,'Address Proof'),(3,'Passport Photo'),
(4,'Aadhaar Card'),(4,'Birth Certificate'),(4,'Address Proof'),(4,'Passport Photo'),
(5,'Aadhaar Card'),(5,'Address Proof'),(5,'Passport Photo'),(5,'Age Proof'),
(6,'Driving License'),(6,'Insurance Policy'),(6,'Address Proof'),(6,'PAN Card'),
(7,'Aadhaar Card'),(7,'PAN Card'),(7,'Address Proof'),(7,'Passport Photo'),
(8,'Hospital Discharge Summary'),(8,'Parents Aadhaar Card'),(8,'Address Proof');
