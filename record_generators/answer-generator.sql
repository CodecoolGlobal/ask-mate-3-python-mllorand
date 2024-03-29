--
-- execute question-generator at least once before execution
--

do $$
    BEGIN
        for cnt in 1..28 loop
                insert into answer(vote_number, question_id, message, image, user_id)
                values(floor(random() * 95 + 5)::int,
                        (SELECT id
                       FROM question
                       ORDER BY random()
                       LIMIT 1),
                       concat('Test Answer Message Nr.: ', cnt),
                       'no_image_found.png',
                       (SELECT user_id
                        FROM users
                        ORDER BY random()
                        LIMIT 1));
            end loop;
    END;$$