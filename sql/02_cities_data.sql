INSERT INTO cities (city_name, country, latitude, longitude, timezone)
VALUES
    ('Dublin',      'Ireland', 53.33306, -6.24889, 'Europe/Dublin'),
    ('Milan',       'Italy',   45.46427,  9.18951, 'Europe/Rome'),
    ('Madrid',      'Spain',   40.41650, -3.70256, 'Europe/Madrid'),
    ('Berlin',      'Germany', 52.52437, 13.41053, 'Europe/Berlin'),
    ('Cluj-Napoca', 'Romania', 46.76667, 23.60000, 'Europe/Bucharest')
ON CONFLICT (city_name, country) DO NOTHING;