CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);



CREATE TABLE person (
    person_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    employment_status ENUM('Employed', 'Unemployed', 'Retired', 'Student') DEFAULT 'Unemployed',
    date_of_birth DATE NOT NULL,
    street VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    phone_no VARCHAR(15) NOT NULL UNIQUE CHECK (phone_no REGEXP '^[0-9]{10}$') -- Phone number should be exactly 10 digits
);

-- Creating the person_phone table (for multiple phone numbers per person)
CREATE TABLE person_phone (
    person_id INT,
    phone_no VARCHAR(15),
    PRIMARY KEY (person_id, phone_no),
    FOREIGN KEY (person_id) REFERENCES person(person_id)
);

-- Creating the salary table with updated constraints
CREATE TABLE salary (
    salary_id INT PRIMARY KEY AUTO_INCREMENT,
    monthly_salary DECIMAL(10, 2) CHECK (monthly_salary > 0), -- Ensure positive salary
    net_salary DECIMAL(10, 2) CHECK (net_salary > 0), -- Net salary must be positive
    deductions DECIMAL(10, 2) DEFAULT 0 CHECK (deductions >= 0), -- Deductions should be non-negative
    salary_date DATE NOT NULL,
    person_id INT,
    FOREIGN KEY (person_id) REFERENCES person(person_id)
);

-- Creating the asset table with updated constraints
CREATE TABLE asset (
    asset_id INT PRIMARY KEY AUTO_INCREMENT,
    asset_name VARCHAR(255) NOT NULL,
    asset_type ENUM('Real Estate', 'Stock', 'Gold', 'Silver', 'Cash', 'Others') NOT NULL,
    purchased_price DECIMAL(12, 2) CHECK (purchased_price > 0),
    current_value DECIMAL(12, 2) CHECK (current_value > 0),
    purchased_date DATE NOT NULL,
    quantity INT DEFAULT 1 CHECK (quantity >= 1),
    status ENUM('Active', 'Sold') DEFAULT 'Active',
    person_id INT,
    FOREIGN KEY (person_id) REFERENCES person(person_id)
);

-- Creating the asset_status table (status for each asset)
CREATE TABLE asset_status (
    asset_id INT,
    status ENUM('Active', 'Sold') DEFAULT 'Active',
    PRIMARY KEY (asset_id, status),
    FOREIGN KEY (asset_id) REFERENCES asset(asset_id)
);

-- Creating the transaction table with updated constraints
CREATE TABLE transaction (
    transaction_id INT PRIMARY KEY AUTO_INCREMENT,
    type ENUM('Credit', 'Debit') NOT NULL,
    amount DECIMAL(12, 2) NOT NULL CHECK (amount > 0),
    date DATE NOT NULL,
    description VARCHAR(255),
    person_id INT,
    asset_id INT,
    FOREIGN KEY (person_id) REFERENCES person(person_id),
    FOREIGN KEY (asset_id) REFERENCES asset(asset_id)
);

-- Creating the market_rate table (rate for each asset)
CREATE TABLE market_rate (
    rate_asset INT, -- FK to ASSET
    rate_value DECIMAL(12, 2) NOT NULL CHECK (rate_value > 0),
    rate_date DATE NOT NULL,
    PRIMARY KEY (rate_asset, rate_date),
    FOREIGN KEY (rate_asset) REFERENCES asset(asset_id)
);

-- Creating the loan table with updated constraints
CREATE TABLE loan (
    loan_id INT PRIMARY KEY AUTO_INCREMENT,
    principal_amount DECIMAL(12, 2) NOT NULL CHECK (principal_amount > 0),
    interest_rate DECIMAL(5, 2) CHECK (interest_rate > 0 AND interest_rate <= 100), -- Interest rate as a percentage (0-100)
    tenure INT NOT NULL CHECK (tenure > 0), -- Tenure in months
    start_date DATE NOT NULL,
    end_date DATE GENERATED ALWAYS AS (DATE_ADD(start_date, INTERVAL tenure MONTH)) STORED, -- Auto-calculated based on tenure
    monthly_emi DECIMAL(12, 2) CHECK (monthly_emi > 0),
    status ENUM('Ongoing', 'Closed', 'Defaulted') DEFAULT 'Ongoing',
    person_id INT,
    FOREIGN KEY (person_id) REFERENCES person(person_id)
);

-- Creating the loan_status table (status for each loan)
CREATE TABLE loan_status (
    loan_id INT,
    status ENUM('Ongoing', 'Closed', 'Defaulted') DEFAULT 'Ongoing',
    PRIMARY KEY(loan_id, status),
    FOREIGN KEY (loan_id) REFERENCES loan(loan_id)
);

-- Creating the own table (relation between assets and loans)
CREATE TABLE own (
    asset_id INT,
    loan_id INT,
    person_id INT,
    PRIMARY KEY (asset_id, loan_id, person_id),
    FOREIGN KEY (asset_id) REFERENCES asset(asset_id),
    FOREIGN KEY (loan_id) REFERENCES loan(loan_id),
    FOREIGN KEY (person_id) REFERENCES person(person_id)
);

-- Creating the emi table with updated constraints
CREATE TABLE emi (
    emi_id INT PRIMARY KEY AUTO_INCREMENT,
    emi_amount DECIMAL(12, 2) NOT NULL CHECK (emi_amount > 0),
    due_date DATE NOT NULL,
    emi_status ENUM('Pending', 'Paid') DEFAULT 'Pending',
    loan_id INT,
    FOREIGN KEY (loan_id) REFERENCES loan(loan_id)
);

-- Inserting into person table
INSERT INTO person (name, employment_status, date_of_birth, street, city, state, phone_no)
VALUES 
('John Doe', 'Employed', '1985-06-15', '123 Maple St', 'Springfield', 'Illinois', '1234567890'),
('Jane Smith', 'Student', '1999-11-30', '456 Oak St', 'Lincoln', 'Nebraska', '2345678901'),
('Mike Brown', 'Unemployed', '1970-01-25', '789 Pine St', 'Dallas', 'Texas', '3456789012'),
('Anna White', 'Retired', '1955-05-12', '321 Birch St', 'Austin', 'Texas', '4567890123'),
('Tom Black', 'Employed', '1989-02-14', '654 Elm St', 'Denver', 'Colorado', '5678901234');

-- Inserting into person_phone table
INSERT INTO person_phone (person_id, phone_no)
VALUES 
(1, '1234567890'),
(2, '2345678901'),
(3, '3456789012'),
(4, '4567890123'),
(5, '5678901234');

-- Inserting into salary table
INSERT INTO salary (monthly_salary, net_salary, deductions, salary_date, person_id)
VALUES 
(5000.00, 4500.00, 500.00, '2024-01-31', 1),
(3000.00, 2800.00, 200.00, '2024-01-31', 2),
(4600.00, 3500.00, 500.00, '2024-01-31', 3), 
(4000.00, 3800.00, 200.00, '2024-01-31', 4),
(5500.00, 5000.00, 500.00, '2024-01-31', 5);

-- Inserting into asset table
INSERT INTO asset (asset_name, asset_type, purchased_price, current_value, purchased_date, quantity, status, person_id)
VALUES 
('House', 'Real Estate', 200000.00, 250000.00, '2020-06-15', 1, 'Active', 1),
('Tesla Stock', 'Stock', 30000.00, 35000.00, '2023-01-10', 10, 'Active', 2),
('Gold', 'Gold', 15000.00, 16000.00, '2021-09-01', 5, 'Sold', 3),
('Silver Coins', 'Silver', 5000.00, 5200.00, '2019-11-20', 100, 'Active', 4),
('Savings', 'Cash', 10000.00, 12000.00, '2022-08-08', 1, 'Active', 5);

-- Inserting into asset_status table
INSERT INTO asset_status (asset_id, status)
VALUES 
(1, 'Active'),
(2, 'Active'),
(3, 'Sold'),
(4, 'Active'),
(5, 'Active');

-- Inserting into transaction table
INSERT INTO transaction (type, amount, date, description, person_id, asset_id)
VALUES 
('Credit', 2000.00, '2024-02-01', 'Salary Credit', 1, 1),
('Debit', 500.00, '2024-02-05', 'Grocery Purchase', 1, NULL),
('Credit', 300.00, '2024-02-10', 'Freelance Work', 2, NULL),
('Debit', 1500.00, '2024-02-12', 'Rent Payment', 4, NULL),
('Credit', 2000.00, '2024-02-15', 'Investment Return', 5, 5);

-- Inserting into market_rate table
INSERT INTO market_rate (rate_asset, rate_value, rate_date)
VALUES 
(1, 250000.00, '2024-02-01'),
(2, 35000.00, '2024-02-01'),
(3, 16000.00, '2024-02-01'),
(4, 5200.00, '2024-02-01'),
(5, 12000.00, '2024-02-01');

-- Inserting into loan table
INSERT INTO loan (principal_amount, interest_rate, tenure, start_date, monthly_emi, status, person_id)
VALUES 
(10000.00, 5.0, 12, '2023-01-01', 870.00, 'Ongoing', 1),
(20000.00, 7.5, 24, '2022-05-15', 923.00, 'Ongoing', 2),
(5000.00, 4.5, 6, '2023-08-01', 865.00, 'Closed', 3),
(30000.00, 6.0, 36, '2021-07-10', 943.00, 'Defaulted', 4),
(25000.00, 5.0, 18, '2023-02-05', 1468.00, 'Ongoing', 5);

-- Inserting into loan_status table
INSERT INTO loan_status (loan_id, status)
VALUES 
(1, 'Ongoing'),
(2, 'Ongoing'),
(3, 'Closed'),
(4, 'Defaulted'),
(5, 'Ongoing');

-- Inserting into own table
INSERT INTO own (asset_id, loan_id, person_id)
VALUES 
(1, 1, 1),
(2, 2, 2),
(3, 3, 3),
(4, 4, 4),
(5, 5, 5);

-- Inserting into emi table
INSERT INTO emi (emi_amount, due_date, emi_status, loan_id)
VALUES 
(870.00, '2024-01-01', 'Paid', 1),
(923.00, '2024-01-15', 'Pending', 2),
(865.00, '2023-08-15', 'Paid', 3),
(943.00, '2023-10-10', 'Pending', 4),
(1468.00, '2024-01-05', 'Pending', 5);