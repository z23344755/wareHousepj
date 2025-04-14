

CREATE TABLE sku (
    id SERIAL PRIMARY KEY,
    sku_code VARCHAR(50) UNIQUE NOT NULL,
    name TEXT,
    description TEXT,
    company VARCHAR(100),
    quantity INT CHECK (quantity >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    sku_code VARCHAR(50)  NOT NULL,
    quantity INT CHECK (quantity >= 0),
    warehouse_location VARCHAR(50),
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    level VARCHAR(50)
);







CREATE TABLE in_out_his (
    id SERIAL PRIMARY KEY,
    sku_code VARCHAR(50)  NOT NULL,
     operate_type VARCHAR(50)  CHECK (operate_type IN ('in', 'out')) DEFAULT 'in',
    quantity INT CHECK (quantity >= 0),
    warehouse_location VARCHAR(50),
     operate_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
         level VARCHAR(50)
);






CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    task_description TEXT NOT NULL,
    status VARCHAR(10) CHECK (status IN ('✔', '✖', '?')) DEFAULT '?',
    related_sku INT ,
    related_container VARCHAR(50),
    due_date TIMESTAMP
);



INSERT INTO sku (sku_code, name, description, company,created_at ,quantity )
VALUES
    ('SKU001', 'Product A', 'High-quality product A for everyday use', 'Company X', '2023-10-01 10:00:00' ,20),
    ('SKU002', 'Product B', 'Eco-friendly product B made from recycled materials', 'Company Y', '2023-10-02 11:30:00',30),
    ('SKU003', 'Product C', 'Premium product C with advanced features', 'Company Z', '2023-10-03 09:15:00',30),
    ('SKU004', 'Product D', 'Affordable product D for budget-conscious buyers', 'Company X', '2023-10-04 14:45:00',30),
    ('SKU005', 'Product E', 'Innovative product E designed for tech enthusiasts', 'Company Y', '2023-10-05 16:20:00',30)



INSERT INTO inventory (sku_code, quantity, warehouse_location, update_time , level)
VALUES
    ('SKU001', 100, 'B1', '2023-10-01 10:05:00' ,'A'),
        ('SKU001', 10, 'B1', '2023-11-01 10:05:00','A'),
    ('SKU002', 75, 'B1', '2023-10-02 11:35:00','B'),
    ('SKU003', 50, 'B2', '2023-10-03 09:20:00','C'),
    ('SKU004', 200, 'B3', '2023-10-04 14:50:00','A'),
    ('SKU005', 30, 'B1', '2023-10-05 16:25:00','F');




     INSERT INTO in_out_his (sku_code, operate_type, quantity, warehouse_location, operate_time ,level)
VALUES
    ('SKU001', 'in', 100, 'Warehouse A', '2023-10-01 10:05:00' ,'A'),
    ('SKU002', 'in', 75, 'Warehouse B', '2023-10-02 11:35:00','A'),
    ('SKU003', 'in', 50, 'Warehouse C', '2023-10-03 09:20:00','A'),
    ('SKU004', 'in', 200, 'Warehouse A', '2023-10-04 14:50:00','A'),
    ('SKU005', 'in', 30, 'Warehouse B', '2023-10-05 16:25:00','A'),
    ('SKU001', 'out', 20, 'Warehouse A', '2023-10-06 09:00:00','A'),
    ('SKU002', 'out', 15, 'Warehouse B', '2023-10-06 10:30:00','A'),
    ('SKU003', 'out', 10, 'Warehouse C', '2023-10-06 11:45:00','A'),
    ('SKU004', 'out', 50, 'Warehouse A', '2023-10-06 14:00:00','A'),
    ('SKU005', 'out', 5, 'Warehouse B', '2023-10-06 15:15:00','A');




   CREATE TABLE warehouse_locations (
    id VARCHAR(200) PRIMARY KEY,
    type VARCHAR(20) NOT NULL,
    location VARCHAR(20) NOT NULL,
    bounds VARCHAR(250) NOT NULL
);




INSERT INTO warehouse_locations (id, type, location, bounds) VALUES
('shelf-B1', 'shelf', 'B1', '0, 240, 10, 250'),
('shelf-B2', 'shelf', 'B2', '0, 250, 10, 260'),
('shelf-B3', 'shelf', 'B3', '0, 260, 10, 270');


  INSERT INTO warehouse_locations (id, type, location, bounds) VALUES
('shelf-C1', 'shelf', 'C1', '10, 240, 20, 250'),
('shelf-C2', 'shelf', 'C2', '10, 250, 20, 260'),
('shelf-C3', 'shelf', 'C3', '10, 260, 20, 270');




select * from warehouse_locations;