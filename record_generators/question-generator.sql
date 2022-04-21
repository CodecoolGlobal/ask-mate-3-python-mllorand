do $$
    BEGIN
        for cnt in 1..7 loop
                insert into question(view_number, vote_number, title, message, image, user_id)
                values(floor(random() * 95 + 5)::int,
                       floor(random() * 95 + 5)::int,
                       concat('Test Question Title Nr.: ', cnt),
                       concat('Test Question Message Nr.: ', cnt),
                       'no_image_found.png',
                       (SELECT user_id
                        FROM users
                        ORDER BY random()
                        LIMIT 1));
            end loop;
    END;$$