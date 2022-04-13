do $$
    BEGIN
        for cnt in 1..7 loop
                insert into comment(question_id, message, edited_count)
                values((SELECT id
                        FROM question
                        ORDER BY random()
                        LIMIT 1),
                       concat('Test comment Nr.:', cnt),
                       floor(random() * 5)::int);
            end loop;
    END;$$

do $$
    BEGIN
        for cnt in 1..7 loop
                insert into comment(answer_id, message, edited_count)
                values((SELECT id
                        FROM answer
                        ORDER BY random()
                        LIMIT 1),
                       concat('Test comment Nr.:', cnt),
                       floor(random() * 5)::int);
            end loop;
    END;$$