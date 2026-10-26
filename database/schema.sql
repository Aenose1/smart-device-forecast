CREATE TABLE devices (
	id VARCHAR(32) NOT NULL, 
	name VARCHAR(160) NOT NULL, 
	brand VARCHAR(80) NOT NULL, 
	category VARCHAR(12) NOT NULL, 
	release_date DATE, 
	launch_price FLOAT NOT NULL, 
	current_price FLOAT, 
	currency VARCHAR(3) NOT NULL, 
	status VARCHAR(14) NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	updated_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_devices_category CHECK (category in ('Laptop','Smartphone')), 
	CONSTRAINT ck_devices_launch_price CHECK (launch_price > 0)
);

CREATE INDEX ix_devices_brand ON devices (brand);

CREATE INDEX ix_devices_category ON devices (category);

CREATE INDEX ix_devices_name ON devices (name);

CREATE TABLE users (
	id SERIAL NOT NULL, 
	email VARCHAR(254) NOT NULL, 
	full_name VARCHAR(120) NOT NULL, 
	password_hash VARCHAR(255) NOT NULL, 
	role VARCHAR(10) NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	token_version INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT ck_users_role CHECK (role in ('user','admin'))
);

CREATE UNIQUE INDEX ix_users_email ON users (email);

CREATE TABLE datasets (
	id SERIAL NOT NULL, 
	filename VARCHAR(255) NOT NULL, 
	stored_path VARCHAR(500) NOT NULL, 
	checksum VARCHAR(64) NOT NULL, 
	uploaded_by INTEGER, 
	is_sample BOOLEAN NOT NULL, 
	rows_total INTEGER NOT NULL, 
	rows_valid INTEGER NOT NULL, 
	rows_invalid INTEGER NOT NULL, 
	rows_duplicate INTEGER NOT NULL, 
	status VARCHAR(20) NOT NULL, 
	report JSON NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(uploaded_by) REFERENCES users (id) ON DELETE SET NULL
);

CREATE TABLE device_specs (
	id SERIAL NOT NULL, 
	device_id VARCHAR(32) NOT NULL, 
	key VARCHAR(60) NOT NULL, 
	value VARCHAR(255) NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_spec_device_key UNIQUE (device_id, key), 
	FOREIGN KEY(device_id) REFERENCES devices (id) ON DELETE CASCADE
);

CREATE INDEX ix_device_specs_device_id ON device_specs (device_id);

CREATE TABLE model_versions (
	id SERIAL NOT NULL, 
	device_id VARCHAR(32) NOT NULL, 
	category VARCHAR(12) NOT NULL, 
	model_type VARCHAR(60) NOT NULL, 
	trained_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	dataset_version VARCHAR(40) NOT NULL, 
	n_observations INTEGER NOT NULL, 
	metrics JSON NOT NULL, 
	candidates JSON NOT NULL, 
	feature_set JSON NOT NULL, 
	artifact_path VARCHAR(500) NOT NULL, 
	is_active BOOLEAN NOT NULL, 
	trained_by INTEGER, 
	PRIMARY KEY (id), 
	FOREIGN KEY(device_id) REFERENCES devices (id) ON DELETE CASCADE, 
	FOREIGN KEY(trained_by) REFERENCES users (id) ON DELETE SET NULL
);

CREATE INDEX ix_model_versions_category ON model_versions (category);

CREATE INDEX ix_model_versions_is_active ON model_versions (is_active);

CREATE INDEX ix_model_versions_device_id ON model_versions (device_id);

CREATE TABLE predictions (
	id SERIAL NOT NULL, 
	user_id INTEGER NOT NULL, 
	device_id VARCHAR(32), 
	model_version_id INTEGER, 
	kind VARCHAR(10) NOT NULL, 
	device_name VARCHAR(160) NOT NULL, 
	brand VARCHAR(80) NOT NULL, 
	category VARCHAR(12) NOT NULL, 
	currency VARCHAR(3) NOT NULL, 
	current_price FLOAT NOT NULL, 
	as_of DATE NOT NULL, 
	horizons JSON NOT NULL, 
	results JSON NOT NULL, 
	path JSON NOT NULL, 
	history JSON NOT NULL, 
	stats JSON NOT NULL, 
	model_info JSON NOT NULL, 
	warnings JSON NOT NULL, 
	is_sample BOOLEAN NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE, 
	FOREIGN KEY(device_id) REFERENCES devices (id) ON DELETE SET NULL, 
	FOREIGN KEY(model_version_id) REFERENCES model_versions (id) ON DELETE SET NULL
);

CREATE INDEX ix_predictions_created_at ON predictions (created_at);

CREATE INDEX ix_predictions_device_id ON predictions (device_id);

CREATE INDEX ix_predictions_user_id ON predictions (user_id);

CREATE TABLE price_history (
	id SERIAL NOT NULL, 
	device_id VARCHAR(32) NOT NULL, 
	date DATE NOT NULL, 
	price FLOAT NOT NULL, 
	source VARCHAR(120) NOT NULL, 
	currency VARCHAR(3) NOT NULL, 
	dataset_id INTEGER, 
	is_sample BOOLEAN NOT NULL, 
	PRIMARY KEY (id), 
	CONSTRAINT uq_price_device_date_source UNIQUE (device_id, date, source), 
	CONSTRAINT ck_price_positive CHECK (price > 0), 
	FOREIGN KEY(device_id) REFERENCES devices (id) ON DELETE CASCADE, 
	FOREIGN KEY(dataset_id) REFERENCES datasets (id) ON DELETE SET NULL
);

CREATE INDEX ix_price_device_date ON price_history (device_id, date);

CREATE INDEX ix_price_history_dataset_id ON price_history (dataset_id);

CREATE TABLE prediction_logs (
	id SERIAL NOT NULL, 
	user_id INTEGER, 
	device_id VARCHAR(32), 
	prediction_id INTEGER, 
	event VARCHAR(30) NOT NULL, 
	status VARCHAR(10) NOT NULL, 
	message TEXT NOT NULL, 
	duration_ms INTEGER NOT NULL, 
	created_at TIMESTAMP WITH TIME ZONE NOT NULL, 
	PRIMARY KEY (id), 
	FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE SET NULL, 
	FOREIGN KEY(device_id) REFERENCES devices (id) ON DELETE SET NULL, 
	FOREIGN KEY(prediction_id) REFERENCES predictions (id) ON DELETE SET NULL
);

CREATE INDEX ix_prediction_logs_device_id ON prediction_logs (device_id);

CREATE INDEX ix_prediction_logs_user_id ON prediction_logs (user_id);

CREATE INDEX ix_prediction_logs_created_at ON prediction_logs (created_at);
