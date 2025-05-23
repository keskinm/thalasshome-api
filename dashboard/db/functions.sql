

CREATE OR REPLACE FUNCTION public.get_availability_calendar_within_75days(
  in_shipping_lon float8,
  in_shipping_lat float8,
  in_product text
)
RETURNS TABLE (
    the_day date,
    remain numeric
)
LANGUAGE sql STABLE AS
$$
WITH client AS (
  SELECT ST_SetSRID(ST_MakePoint(in_shipping_lon, in_shipping_lat), 4326)::geography AS client_geog
),
relevant_users AS (
  SELECT DISTINCT udz.user_id
  FROM user_delivery_zones udz
  JOIN client c ON true
  WHERE ST_DWithin(
    udz.center_geog,
    c.client_geog,
    udz.radius_km * 1000
  )
),
days AS (
  SELECT generate_series(
    CURRENT_DATE,
    CURRENT_DATE + interval '75 days',
    interval '1 day'
  )::date AS d
),
capacity AS (
  SELECT SUM(dc.quantity) AS max_stock
  FROM delivery_capacity dc
  JOIN relevant_users ru ON ru.user_id = dc.user_id
  WHERE dc.product::text = in_product
),
bookings AS (
  SELECT li.from_date, li.to_date, li.quantity
  FROM orders o
  JOIN line_items li ON li.order_id = o.id
  WHERE li.product::text = in_product
    AND li.to_date >= CURRENT_DATE
    AND o.status NOT IN ('canceled')
    AND (
      -- CAS 1 : commande assignée
      (o.delivery_men_id IS NOT NULL
        AND o.delivery_men_id IN (SELECT user_id FROM relevant_users))

      OR
      -- CAS 2 : commande non assignée mais physiquement dans la zone couverte
      (o.delivery_men_id IS NULL
       AND EXISTS (
         SELECT 1
         FROM user_delivery_zones z
         JOIN relevant_users ru ON ru.user_id = z.user_id
         WHERE ST_DWithin(
           z.center_geog,
           ST_SetSRID(ST_MakePoint(o.shipping_lon, o.shipping_lat), 4326)::geography,
           z.radius_km * 1000
         )
       ))
    )
)
SELECT
  d AS the_day,
  capacity.max_stock - COALESCE(SUM(bookings.quantity), 0) AS remain
FROM days
CROSS JOIN capacity
LEFT JOIN bookings
       ON d BETWEEN bookings.from_date AND bookings.to_date
GROUP BY d, capacity.max_stock
ORDER BY d;
$$;



------------------------------------------------------------------



CREATE OR REPLACE FUNCTION public.check_delivery_men_around_point(
  in_shipping_lon float8,
  in_shipping_lat float8
)
RETURNS SETOF users
LANGUAGE sql STABLE AS
$$
WITH client AS (
  SELECT ST_SetSRID(ST_MakePoint(in_shipping_lon, in_shipping_lat), 4326)::geography AS client_geog
)
SELECT DISTINCT ON (u.id) u.*
FROM user_delivery_zones udz
JOIN client c ON ST_DWithin(
  udz.center_geog,
  c.client_geog,
  udz.radius_km * 1000
)
JOIN users u ON udz.user_id = u.id
ORDER BY u.id;
$$;
