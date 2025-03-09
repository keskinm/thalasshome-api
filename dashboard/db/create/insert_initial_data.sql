INSERT INTO users (username, password, email, is_staff, country, zone, phone_number) VALUES
('python', 'pbkdf2:sha256:1000000$3DdeCIsJlSyGs1Bi$9743fe7068be6602cab76b03edfdab326bdf62fe89793e5832098801a13db4ca', 'neuneu@yopmail.com', true, 'France', 'ile_de_france', '+33666666666'),
('python2', 'pbkdf2:sha256:1000000$3DdeCIsJlSyGs1Bi$9743fe7068be6602cab76b03edfdab326bdf62fe89793e5832098801a13db4ca', 'neuneu2@yopmail.com', true, 'France', 'var', '+33666666666'),
('python3', 'pbkdf2:sha256:1000000$3DdeCIsJlSyGs1Bi$9743fe7068be6602cab76b03edfdab326bdf62fe89793e5832098801a13db4ca', 'neuneu3@yopmail.com', true, 'France', 'pays_de_gex', '+33666666666'),
('python4', 'pbkdf2:sha256:1000000$3DdeCIsJlSyGs1Bi$9743fe7068be6602cab76b03edfdab326bdf62fe89793e5832098801a13db4ca', 'neuneu4@yopmail.com', true, 'France', 'loire', '+33666666666');


DO $$
DECLARE
    user1_id INT;
    user2_id INT;
    user3_id INT;
    user4_id INT;
BEGIN
    SELECT id INTO user1_id FROM users WHERE username = 'python';
    SELECT id INTO user2_id FROM users WHERE username = 'python2';
    SELECT id INTO user3_id FROM users WHERE username = 'python3';
    SELECT id INTO user4_id FROM users WHERE username = 'python4';

    -- Insertion des données dans la table user_delivery_zones
    INSERT INTO user_delivery_zones (user_id, zone_name, center_geog, radius_km) VALUES
    (user1_id, 'ile_de_france', ST_GeogFromText('SRID=4326;POINT(2.3522 48.8566)'), 30),
    (user2_id, 'var', ST_GeogFromText('SRID=4326;POINT(5.9280 43.1242)'), 30),
    (user3_id, 'pays_de_gex', ST_GeogFromText('SRID=4326;POINT(6.0167 46.3333)'), 30),
    (user4_id, 'loire', ST_GeogFromText('SRID=4326;POINT(4.31 45.39)'), 30);

    -- Insertion des données dans la table delivery_capacity
    INSERT INTO delivery_capacity (user_id, product, quantity) VALUES
    (user1_id, 'jacuzzi6p', 1),
    (user1_id, 'jacuzzi4p', 1),
    (user2_id, 'jacuzzi6p', 1),
    (user2_id, 'jacuzzi4p', 1),
    (user3_id, 'jacuzzi6p', 1),
    (user3_id, 'jacuzzi4p', 1),
    (user4_id, 'jacuzzi6p', 1),
    (user4_id, 'jacuzzi4p', 1);
END $$;
