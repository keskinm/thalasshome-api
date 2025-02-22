CREATE OR REPLACE FUNCTION get_user_by_zone(command_zone text)
RETURNS SETOF users
LANGUAGE sql
AS $$
  SELECT * FROM users
   WHERE users.zone = command_zone;
$$;



------------------------------------------------------------------