CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  username TEXT UNIQUE,
  password TEXT,
  cnic TEXT,
  make_name TEXT
);

CREATE TABLE vehicle_inspection (
  id SERIAL PRIMARY KEY,
  user_id INTEGER,
  client_name TEXT,
  make_name TEXT,
  sub_make_name TEXT,
  model_year INTEGER,
  tracker_id INTEGER,
  suminsured FLOAT,
  grosspremium FLOAT,
  netpremium FLOAT,
  no_of_claims INTEGER,
  clam_amount FLOAT
);

CREATE TABLE vehicle_risk (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    driver_age INTEGER,
    vehicle_make TEXT,
    vehicle_variant TEXT,
    model_year INTEGER,
    capacity INTEGER,
    num_claims INTEGER,
    risk_level TEXT,
    premium_rate REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
