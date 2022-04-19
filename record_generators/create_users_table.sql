create table users
(
    user_id           serial
        constraint users_pk
            primary key,
    user_name         varchar(100) not null,
    email             varchar(120) not null,
    password          varchar(200) not null,
    registration_date timestamp    not null
);


create unique index users_email_uindex
    on users (email);

create unique index users_user_id_uindex
    on users (user_id);

create unique index users_user_name_uindex
    on users (user_name);
