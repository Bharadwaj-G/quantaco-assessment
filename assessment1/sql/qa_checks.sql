-- QA checks on the weather table, for output consistency to frontend consumers.
-- Each SELECT returns violating rows; an empty result set means that check passes.

-- 1. Range checks: percentages must be 0-100 (or null), physical quantities can't be negative.
SELECT id, venue_id, datetime, 'relative_humidity_2m out of range' AS violation
FROM weather
WHERE relative_humidity_2m IS NOT NULL
  AND (relative_humidity_2m < 0 OR relative_humidity_2m > 100)

UNION ALL
SELECT id, venue_id, datetime, 'precipitation_probability out of range'
FROM weather
WHERE precipitation_probability IS NOT NULL
  AND (precipitation_probability < 0 OR precipitation_probability > 100)

UNION ALL
SELECT id, venue_id, datetime, 'negative precipitation'
FROM weather
WHERE precipitation IS NOT NULL AND precipitation < 0

UNION ALL
SELECT id, venue_id, datetime, 'negative rain'
FROM weather
WHERE rain IS NOT NULL AND rain < 0

UNION ALL
SELECT id, venue_id, datetime, 'negative showers'
FROM weather
WHERE showers IS NOT NULL AND showers < 0

UNION ALL
SELECT id, venue_id, datetime, 'negative snowfall'
FROM weather
WHERE snowfall IS NOT NULL AND snowfall < 0

UNION ALL
SELECT id, venue_id, datetime, 'negative snow_depth'
FROM weather
WHERE snow_depth IS NOT NULL AND snow_depth < 0

-- 2. Cross-field consistency: precipitation = rain + showers + snowfall
--    (snowfall is in cm, everything else here is in mm - divide by 7 for its
--    water-equivalent in mm, per Open-Meteo's docs).
UNION ALL
SELECT id, venue_id, datetime, 'precipitation != rain + showers + snowfall/7'
FROM weather
WHERE precipitation IS NOT NULL
  AND rain IS NOT NULL
  AND showers IS NOT NULL
  AND snowfall IS NOT NULL
  AND ABS(precipitation - (rain + showers + snowfall / 7.0)) > 0.1

-- 3. No duplicate (venue_id, datetime) pairs
UNION ALL
SELECT MIN(id), venue_id, datetime, 'duplicate venue_id + datetime'
FROM weather
GROUP BY venue_id, datetime
HAVING COUNT(*) > 1

-- 4. Referential integrity: every weather.venue_id must exist in venue
--    (on top of the FK constraint).
UNION ALL
SELECT w.id, w.venue_id, w.datetime, 'venue_id not found in venue table'
FROM weather w
LEFT JOIN venue v ON v.id = w.venue_id
WHERE v.id IS NULL

ORDER BY venue_id, datetime;
