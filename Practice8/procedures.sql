
-- PROCEDURE 1: Insert or Update user

CREATE OR REPLACE PROCEDURE insert_or_update_user(
    p_name TEXT,
    p_phone TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM phonebook WHERE name = p_name) THEN
        UPDATE phonebook
        SET phone = p_phone
        WHERE name = p_name;
    ELSE
        INSERT INTO phonebook(name, phone)
        VALUES (p_name, p_phone);
    END IF;
END;
$$;



-- PROCEDURE 2: Insert many users with validation


CREATE OR REPLACE PROCEDURE insert_many_users(
    names TEXT[],
    phones TEXT[]
)
LANGUAGE plpgsql
AS $$
DECLARE
    i INT;
BEGIN
    FOR i IN 1..array_length(names,1) LOOP

        -- Validate phone (only digits allowed)
        IF phones[i] ~ '^[0-9]+$' THEN

            IF EXISTS (SELECT 1 FROM phonebook WHERE name = names[i]) THEN
                UPDATE phonebook
                SET phone = phones[i]
                WHERE name = names[i];
            ELSE
                INSERT INTO phonebook(name, phone)
                VALUES (names[i], phones[i]);
            END IF;

        ELSE
            RAISE NOTICE 'Incorrect phone: % for user %', phones[i], names[i];
        END IF;

    END LOOP;
END;
$$;




-- PROCEDURE 3: Delete by name OR phone


CREATE OR REPLACE PROCEDURE delete_user(
    p_value TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM phonebook
    WHERE name = p_value
       OR phone = p_value;
END;
$$;