do $$
    BEGIN
        for cnt in 1..97 loop
                insert into question(view_number, vote_number, title, message, image)
                values(floor(random() * 95 + 5)::int,
                       floor(random() * 95 + 5)::int,
                       concat('Test Question Title Nr.: ', cnt),
                       concat('Test Question Message Nr.: ', cnt),
                       'no_image_found.png');
            end loop;
    END;$$