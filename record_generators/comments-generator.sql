do $$
    BEGIN
        for cnt in 1..200 loop
                insert into comment(question_id, message, edited_count, user_id)
                values((SELECT id
                        FROM question
                        ORDER BY random()
                        LIMIT 1),
                       concat('Test comment Nr.:', cnt),
                       floor(random() * 5)::int,
                       (SELECT user_id
                        FROM users
                        ORDER BY random()
                        LIMIT 1));
            end loop;
    END;$$

do $$
    BEGIN
        for cnt in 1..200 loop
                insert into comment(answer_id, message, edited_count, user_id)
                values((SELECT id
                        FROM answer
                        ORDER BY random()
                        LIMIT 1),
                       concat('Test comment Nr.:', cnt),
                       floor(random() * 5)::int,
                       (SELECT user_id
                        FROM users
                        ORDER BY random()
                        LIMIT 1));
            end loop;
    END;$$