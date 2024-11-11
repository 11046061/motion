CREATE DATABASE `sql_sports`;
USE `sql_sports`;
CREATE TABLE `members` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    age INT,
    gender enum('男','女') NOT NULL,
    address VARCHAR(255)
);

INSERT INTO `members` VALUES(1,11046061,11046061,'11046061@ntub.edu.tw','江承恩',21,'男','北商');

SELECT * FROM `members`;
DESCRIBE `members`;




