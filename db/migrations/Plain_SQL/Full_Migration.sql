BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> bb72c556c937

CREATE TABLE categories (
    id SERIAL NOT NULL, 
    title VARCHAR NOT NULL, 
    PRIMARY KEY (id)
);

CREATE TABLE locations (
    location_id SERIAL NOT NULL, 
    address VARCHAR NOT NULL, 
    PRIMARY KEY (location_id)
);

CREATE TABLE users (
    telegram_id INTEGER NOT NULL, 
    name VARCHAR NOT NULL, 
    surname VARCHAR NOT NULL, 
    is_admin BOOLEAN NOT NULL, 
    PRIMARY KEY (telegram_id)
);

CREATE TABLE books (
    book_id SERIAL NOT NULL, 
    title VARCHAR NOT NULL, 
    description VARCHAR NOT NULL, 
    author VARCHAR NOT NULL, 
    owner_id INTEGER NOT NULL, 
    location_id INTEGER NOT NULL, 
    created TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (book_id), 
    FOREIGN KEY(location_id) REFERENCES locations (location_id) ON DELETE CASCADE, 
    FOREIGN KEY(owner_id) REFERENCES users (telegram_id) ON DELETE CASCADE
);

CREATE TABLE wishlists (
    wish_list_id SERIAL NOT NULL, 
    user_id INTEGER NOT NULL, 
    book_title VARCHAR NOT NULL, 
    author VARCHAR NOT NULL, 
    comment VARCHAR, 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (wish_list_id), 
    FOREIGN KEY(user_id) REFERENCES users (telegram_id) ON DELETE CASCADE
);

CREATE TABLE books_categories (
    id SERIAL NOT NULL, 
    book_id INTEGER NOT NULL, 
    category_id INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(book_id) REFERENCES books (book_id) ON DELETE CASCADE, 
    FOREIGN KEY(category_id) REFERENCES categories (id) ON DELETE CASCADE
);

CREATE TABLE orders (
    order_id SERIAL NOT NULL, 
    telegram_id INTEGER NOT NULL, 
    book_id INTEGER NOT NULL, 
    status VARCHAR(10) NOT NULL, 
    taken_from_id INTEGER, 
    returned_to_id INTEGER, 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (order_id), 
    FOREIGN KEY(book_id) REFERENCES books (book_id) ON DELETE CASCADE, 
    FOREIGN KEY(returned_to_id) REFERENCES locations (location_id) ON DELETE SET NULL, 
    FOREIGN KEY(taken_from_id) REFERENCES locations (location_id) ON DELETE SET NULL, 
    FOREIGN KEY(telegram_id) REFERENCES users (telegram_id) ON DELETE CASCADE
);

INSERT INTO alembic_version (version_num) VALUES ('bb72c556c937') RETURNING alembic_version.version_num;

-- Running upgrade bb72c556c937 -> fac7eb737fb2

ALTER TABLE books ALTER COLUMN owner_id TYPE BIGINT;

ALTER TABLE orders ALTER COLUMN telegram_id TYPE BIGINT;

ALTER TABLE users ALTER COLUMN telegram_id TYPE BIGINT;

ALTER TABLE wishlists ALTER COLUMN user_id TYPE BIGINT;

UPDATE alembic_version SET version_num='fac7eb737fb2' WHERE alembic_version.version_num = 'bb72c556c937';

-- Running upgrade fac7eb737fb2 -> ab369facdc5e

ALTER TABLE books_categories DROP CONSTRAINT books_categories_category_id_fkey;

ALTER TABLE books_categories DROP COLUMN category_id;

DROP TABLE categories;

ALTER TABLE books_categories ADD COLUMN category VARCHAR(23) NOT NULL;

UPDATE alembic_version SET version_num='ab369facdc5e' WHERE alembic_version.version_num = 'fac7eb737fb2';

-- Running upgrade ab369facdc5e -> 733567ada7c5

ALTER TABLE locations ADD COLUMN city VARCHAR(13) NOT NULL;

ALTER TABLE locations ADD COLUMN room VARCHAR NOT NULL;

ALTER TABLE locations DROP COLUMN address;

UPDATE alembic_version SET version_num='733567ada7c5' WHERE alembic_version.version_num = 'ab369facdc5e';

-- Running upgrade 733567ada7c5 -> 5cf5a4f8f0b2

ALTER TABLE books ADD COLUMN qr_code BYTEA;

ALTER TABLE locations ADD COLUMN qr_code BYTEA;

UPDATE alembic_version SET version_num='5cf5a4f8f0b2' WHERE alembic_version.version_num = '733567ada7c5';

-- Running upgrade 5cf5a4f8f0b2 -> d90379c34d5b

CREATE TABLE employees (
    id UUID NOT NULL, 
    full_name VARCHAR NOT NULL, 
    email VARCHAR NOT NULL, 
    is_verified BOOLEAN DEFAULT false NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (email)
);

CREATE TABLE permissions (
    id UUID NOT NULL, 
    name VARCHAR NOT NULL, 
    description VARCHAR, 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (name)
);

CREATE TABLE roles (
    id UUID NOT NULL, 
    name VARCHAR NOT NULL, 
    description VARCHAR, 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (name)
);

CREATE TABLE tg_users (
    id UUID NOT NULL, 
    telegram_id VARCHAR NOT NULL, 
    username VARCHAR NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (telegram_id)
);

CREATE TABLE app_users (
    id UUID NOT NULL, 
    tg_user_id UUID NOT NULL, 
    employee_id UUID NOT NULL, 
    role_id UUID NOT NULL, 
    is_active BOOLEAN DEFAULT true NOT NULL, 
    last_seen_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now() NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(employee_id) REFERENCES employees (id), 
    FOREIGN KEY(role_id) REFERENCES roles (id), 
    FOREIGN KEY(tg_user_id) REFERENCES tg_users (id)
);

CREATE TABLE role_permissions (
    role_id UUID NOT NULL, 
    permission_id UUID NOT NULL, 
    PRIMARY KEY (role_id, permission_id), 
    FOREIGN KEY(permission_id) REFERENCES permissions (id) ON DELETE CASCADE, 
    FOREIGN KEY(role_id) REFERENCES roles (id) ON DELETE CASCADE
);

ALTER TABLE books_categories DROP CONSTRAINT books_categories_book_id_fkey;

ALTER TABLE orders DROP CONSTRAINT orders_book_id_fkey;

ALTER TABLE books DROP CONSTRAINT books_location_id_fkey;

ALTER TABLE orders DROP CONSTRAINT orders_taken_from_id_fkey;

ALTER TABLE orders DROP CONSTRAINT orders_returned_to_id_fkey;

ALTER TABLE locations DROP CONSTRAINT locations_pkey;

ALTER TABLE locations DROP COLUMN location_id;

ALTER TABLE locations ADD COLUMN id UUID NOT NULL;

ALTER TABLE locations ADD CONSTRAINT locations_pkey PRIMARY KEY (id);

ALTER TABLE books DROP CONSTRAINT books_pkey;

ALTER TABLE books DROP COLUMN book_id;

ALTER TABLE books ADD COLUMN id UUID NOT NULL;

ALTER TABLE books ADD CONSTRAINT books_pkey PRIMARY KEY (id);

ALTER TABLE books ALTER COLUMN description DROP NOT NULL;

ALTER TABLE books DROP CONSTRAINT books_owner_id_fkey;

ALTER TABLE books DROP COLUMN owner_id;

ALTER TABLE books ADD COLUMN owner_id UUID NOT NULL;

ALTER TABLE books ADD CONSTRAINT books_owner_id_fkey FOREIGN KEY(owner_id) REFERENCES app_users (id) ON DELETE CASCADE;

ALTER TABLE books DROP COLUMN location_id;

ALTER TABLE books ADD COLUMN location_id UUID NOT NULL;

ALTER TABLE books ADD CONSTRAINT books_location_id_fkey FOREIGN KEY(location_id) REFERENCES locations (id) ON DELETE CASCADE;

ALTER TABLE books_categories DROP CONSTRAINT books_categories_pkey;

ALTER TABLE books_categories DROP COLUMN id;

ALTER TABLE books_categories ADD COLUMN id UUID NOT NULL;

ALTER TABLE books_categories ADD CONSTRAINT books_categories_pkey PRIMARY KEY (id);

ALTER TABLE books_categories DROP COLUMN book_id;

ALTER TABLE books_categories ADD COLUMN book_id UUID NOT NULL;

ALTER TABLE books_categories ADD CONSTRAINT books_categories_book_id_fkey FOREIGN KEY(book_id) REFERENCES books (id) ON DELETE CASCADE;

ALTER TABLE orders DROP CONSTRAINT orders_pkey;

ALTER TABLE orders DROP COLUMN order_id;

ALTER TABLE orders ADD COLUMN id UUID NOT NULL;

ALTER TABLE orders ADD CONSTRAINT orders_pkey PRIMARY KEY (id);

ALTER TABLE orders DROP CONSTRAINT orders_telegram_id_fkey;

ALTER TABLE orders DROP COLUMN telegram_id;

ALTER TABLE orders ADD COLUMN app_user_id UUID NOT NULL;

ALTER TABLE orders ADD CONSTRAINT orders_app_user_id_fkey FOREIGN KEY(app_user_id) REFERENCES app_users (id) ON DELETE CASCADE;

ALTER TABLE orders DROP COLUMN book_id;

ALTER TABLE orders ADD COLUMN book_id UUID NOT NULL;

ALTER TABLE orders ADD CONSTRAINT orders_book_id_fkey FOREIGN KEY(book_id) REFERENCES books (id) ON DELETE CASCADE;

ALTER TABLE orders DROP COLUMN taken_from_id;

ALTER TABLE orders ADD COLUMN taken_from_id UUID;

ALTER TABLE orders ADD CONSTRAINT orders_taken_from_id_fkey FOREIGN KEY(taken_from_id) REFERENCES locations (id) ON DELETE SET NULL;

ALTER TABLE orders DROP COLUMN returned_to_id;

ALTER TABLE orders ADD COLUMN returned_to_id UUID;

ALTER TABLE orders ADD CONSTRAINT orders_returned_to_id_fkey FOREIGN KEY(returned_to_id) REFERENCES locations (id) ON DELETE SET NULL;

ALTER TABLE wishlists DROP CONSTRAINT wishlists_pkey;

ALTER TABLE wishlists DROP COLUMN wish_list_id;

ALTER TABLE wishlists ADD COLUMN id UUID NOT NULL;

ALTER TABLE wishlists ADD CONSTRAINT wishlists_pkey PRIMARY KEY (id);

ALTER TABLE wishlists DROP CONSTRAINT wishlists_user_id_fkey;

ALTER TABLE wishlists DROP COLUMN user_id;

ALTER TABLE wishlists ADD COLUMN app_user_id UUID NOT NULL;

ALTER TABLE wishlists ADD CONSTRAINT wishlists_app_user_id_fkey FOREIGN KEY(app_user_id) REFERENCES app_users (id) ON DELETE CASCADE;

DROP TABLE users;

UPDATE alembic_version SET version_num='d90379c34d5b' WHERE alembic_version.version_num = '5cf5a4f8f0b2';

COMMIT;
