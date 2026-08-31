-- Given sample venue data.

INSERT INTO venue (id, name, latitude, longitude) VALUES
    (1, 'Venue1', 52.52,   13.41),
    (2, 'Venue2', -30,     153.125),
    (3, 'Venue3', 44.4375, 26.125)
ON CONFLICT (id) DO UPDATE SET
    name      = EXCLUDED.name,
    latitude  = EXCLUDED.latitude,
    longitude = EXCLUDED.longitude;
