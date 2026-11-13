-- MySQL 8: same schema initialized by src.utils.database.init_db on startup.
CREATE TABLE IF NOT EXISTS datasets (id BIGINT PRIMARY KEY AUTO_INCREMENT, natural_key VARCHAR(180) UNIQUE NOT NULL, payload LONGTEXT NOT NULL, created_at VARCHAR(40) NOT NULL);
CREATE TABLE IF NOT EXISTS scenarios LIKE datasets;
CREATE TABLE IF NOT EXISTS runs LIKE datasets;
CREATE TABLE IF NOT EXISTS plans LIKE datasets;
CREATE TABLE IF NOT EXISTS reports LIKE datasets;
CREATE TABLE IF NOT EXISTS users LIKE datasets;
CREATE TABLE IF NOT EXISTS audit LIKE datasets;

CREATE TABLE IF NOT EXISTS schedules LIKE datasets;
CREATE TABLE IF NOT EXISTS delivery_snapshots LIKE datasets;
