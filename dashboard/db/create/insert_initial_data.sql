INSERT INTO users (username, password, email, is_staff, country, zone, phone_number) VALUES
('python', 'pbkdf2:sha256:1000000$SHQVsanyO7Nb07oQ$63a83e27956014ec3bcbab3bb28ef8afa6c30c79a8dffc77f413c969499b56b5', 'none@yopmail.com', true, 'France', 'ile_de_france', '+33666666666'),
('python2', 'pbkdf2:sha256:1000000$SHQVsanyO7Nb07oQ$63a83e27956014ec3bcbab3bb28ef8afa6c30c79a8dffc77f413c969499b56b5', 'none2@yopmail.com', true, 'France', 'var', '+33666666666'),
('python3', 'pbkdf2:sha256:1000000$SHQVsanyO7Nb07oQ$63a83e27956014ec3bcbab3bb28ef8afa6c30c79a8dffc77f413c969499b56b5', 'none3@yopmail.com', true, 'France', 'pays_de_gex', '+33666666666'),
('python4', 'pbkdf2:sha256:1000000$SHQVsanyO7Nb07oQ$63a83e27956014ec3bcbab3bb28ef8afa6c30c79a8dffc77f413c969499b56b5', 'none4@yopmail.com', true, 'France', 'loire', '+33666666666');


INSERT INTO user_delivery_zones (user_id, zone_name, center_geog, radius_km) VALUES
(1, 'ile_de_france', ST_GeogFromText('SRID=4326;POINT(2.3522 48.8566)'), 30),
(2, 'var', ST_GeogFromText('SRID=4326;POINT(5.9280 43.1242)'), 30),
(3, 'pays_de_gex', ST_GeogFromText('SRID=4326;POINT(6.0167 46.3333)'), 30),
(4, 'loire', ST_GeogFromText('SRID=4326;POINT(4.31 45.39)'), 30);


INSERT INTO delivery_stock (user_id, product, quantity) VALUES
(1, 'jacuzzi2p', 1),
(1, 'jacuzzi4p', 1),
(2, 'jacuzzi2p', 1),
(2, 'jacuzzi4p', 1),
(3, 'jacuzzi2p', 1),
(3, 'jacuzzi4p', 1),
(4, 'jacuzzi2p', 1),
(4, 'jacuzzi4p', 1);

