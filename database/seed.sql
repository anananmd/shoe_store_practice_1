INSERT INTO roles (name) VALUES
('guest'),
('client'),
('manager'),
('admin');

INSERT INTO users (username, password, full_name, role_id) VALUES
('client', '123', 'Клиент', 2),
('manager', '123', 'Менеджер', 3),
('admin', '123', 'Администратор', 4);

INSERT INTO categories (name) VALUES
('Кроссовки'),
('Ботинки'),
('Туфли');

INSERT INTO manufacturers (name) VALUES
('Nike'),
('Adidas'),
('Puma');

INSERT INTO suppliers (name) VALUES
('ООО Спорт'),
('ООО Обувь');

INSERT INTO units (name) VALUES
('пара');

INSERT INTO products (
    article,
    name,
    category_id,
    description,
    manufacturer_id,
    supplier_id,
    price,
    discount_percent,
    quantity_in_stock,
    unit_id,
    image_path
) VALUES
('A001', 'Nike Air', 1, 'Кроссовки', 1, 1, 8990, 10, 5, 1, ''),
('A002', 'Adidas Street', 1, 'Кроссовки', 2, 2, 7990, 20, 3, 1, ''),
('A003', 'Puma Classic', 2, 'Ботинки', 3, 1, 9990, 0, 0, 1, '');