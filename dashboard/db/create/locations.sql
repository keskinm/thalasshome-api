CREATE TABLE user_delivery_zones (
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    zone_name TEXT NOT NULL,
    center_lat FLOAT NOT NULL,
    center_lon FLOAT NOT NULL,
    radius_km FLOAT NOT NULL DEFAULT 30,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
