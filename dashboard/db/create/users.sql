CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    is_staff BOOLEAN DEFAULT FALSE,
    country TEXT,
    zone TEXT,
    phone_number TEXT
);
