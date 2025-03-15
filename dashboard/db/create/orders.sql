CREATE TYPE product_type AS ENUM ('jacuzzi6p', 'jacuzzi4p', 'other');

CREATE TYPE order_status AS ENUM (
  'ask', 'pending', 'assigned', 'in_delivery', 'delivered', 'canceled'
);

CREATE TABLE orders (
    id BIGINT PRIMARY KEY,
    email        TEXT,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_price  NUMERIC,
    shipping_address JSONB, -- or JSON?
    phone        TEXT,
    status       order_status DEFAULT 'ask',
    shipping_lat FLOAT,
    shipping_lon FLOAT,
    shipping_phone   TEXT,
    delivery_men_id INTEGER,

    CONSTRAINT fk_delivery_men_id
      FOREIGN KEY (delivery_men_id)
      REFERENCES users(id)
);


CREATE TABLE line_items (
    id BIGINT PRIMARY KEY,
    order_id   BIGINT NOT NULL,
    from_date DATE,
    to_date DATE,
    quantity   INT,
    price      NUMERIC,
    product    product_type NOT NULL,

    CONSTRAINT fk_order
      FOREIGN KEY (order_id)
      REFERENCES orders(id)
      ON DELETE CASCADE
);


CREATE TABLE delivery_capacity (
    id SERIAL UNIQUE,
    user_id INT NOT NULL,
    product product_type NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    PRIMARY KEY (user_id, product),
    CONSTRAINT fk_delivery_user
      FOREIGN KEY (user_id)
      REFERENCES users(id)
);
