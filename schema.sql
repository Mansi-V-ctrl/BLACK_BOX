CREATE DATABASE IF NOT EXISTS black_box;
USE black_box;

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS applications (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS events (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL,
    user_id INT,
    event_type VARCHAR(100) NOT NULL,
    status VARCHAR(30) NOT NULL,
    description VARCHAR(255),
    event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(application_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS incidents (
    incident_id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description VARCHAR(255),
    severity VARCHAR(20) NOT NULL,
    status VARCHAR(30) DEFAULT 'OPEN',
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (application_id) REFERENCES applications(application_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS incident_events (
    incident_id INT NOT NULL,
    event_id INT NOT NULL,
    PRIMARY KEY (incident_id, event_id),
    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id),
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);

CREATE TABLE IF NOT EXISTS resolutions (
    incident_id INT PRIMARY KEY,
    root_cause VARCHAR(255),
    resolution VARCHAR(255),
    resolved_by INT,
    resolved_at TIMESTAMP NULL,
    FOREIGN KEY (incident_id) REFERENCES incidents(incident_id),
    FOREIGN KEY (resolved_by) REFERENCES users(user_id)
);

INSERT INTO applications (name, description)
SELECT 'Demo Payment App', 'Simulated application used to generate events for BLACK BOX'
WHERE NOT EXISTS (
    SELECT 1 FROM applications WHERE name = 'Demo Payment App'
);