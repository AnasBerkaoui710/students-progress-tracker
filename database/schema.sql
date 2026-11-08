
CREATE DATABASE smart_student_tracking;

USE smart_student_tracking;

-- Students table
CREATE TABLE students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fullname VARCHAR(150) NOT NULL,
    educational_level ENUM('Collège', 'Lycée') NOT NULL
);

-- Monthly tracking table
CREATE TABLE monthly_tracking (
    id INT AUTO_INCREMENT PRIMARY KEY,

    student_id INT NOT NULL,

    tracking_month DATE NOT NULL,

    avg_study_hours DECIMAL(4,2) NOT NULL,
    avg_phone_usage_hours DECIMAL(4,2) NOT NULL,

    study_hours_limit DECIMAL(4,2) NOT NULL,
    phone_usage_limit DECIMAL(4,2) NOT NULL,

    FOREIGN KEY (student_id)
        REFERENCES students(id)
        ON DELETE CASCADE,

    UNIQUE (student_id, tracking_month)
);
