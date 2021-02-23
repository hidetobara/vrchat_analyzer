CREATE DATABASE IF NOT EXISTS vrchat;
CREATE TABLE IF NOT EXISTS vrchat.worlds(
  `id` varchar(64) NOT NULL,
  `name` varchar(128) NOT NULL,
  `author_id` varchar(64) NOT NULL,
  `author_name` varchar(128) NOT NULL,
  `description` varchar(255),
  `thumbnail_image_url` varchar(255),
  `favorites` integer,
  `created_at` datetime,
  `updated_at` datetime,
  `published_at` datetime,
  PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
