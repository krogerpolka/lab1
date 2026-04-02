
-- FUNCTION 1: Search by pattern


CREATE OR REPLACE FUNCTION search_phonebook(pattern TEXT)
RETURNS TABLE(
    id INT,
    name VARCHAR,
    phone VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, p.name, p.phone
    FROM phonebook p
    WHERE p.name ILIKE '%' || pattern || '%'
       OR p.phone LIKE '%' || pattern || '%';
END;
$$;


-- FUNCTION 2: Pagination (LIMIT / OFFSET)


CREATE OR REPLACE FUNCTION get_phonebook_page(
    limit_count INT,
    offset_count INT
)
RETURNS TABLE(
    id INT,
    name VARCHAR,
    phone VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT p.id, p.name, p.phone
    FROM phonebook p
    ORDER BY p.id
    LIMIT limit_count
    OFFSET offset_count;
END;
$$;