USE black_box;

SELECT * FROM users;

SELECT * FROM applications;

SELECT * FROM events;

SELECT
    e.event_id,
    a.name AS application,
    e.event_type,
    e.status,
    e.event_time
FROM events e
JOIN applications a
ON e.application_id = a.application_id
ORDER BY e.event_time DESC;

SELECT
    status,
    COUNT(*) AS total_events
FROM events
GROUP BY status;

SELECT
    severity,
    COUNT(*) AS total_incidents
FROM incidents
GROUP BY severity;

SELECT
    i.incident_id,
    i.title,
    i.severity,
    i.status,
    a.name AS application
FROM incidents i
JOIN applications a
ON i.application_id = a.application_id;

SELECT
    e.event_type,
    e.status,
    e.description,
    e.event_time
FROM events e
JOIN incident_events ie
ON e.event_id = ie.event_id
WHERE ie.incident_id = 1
ORDER BY e.event_time;