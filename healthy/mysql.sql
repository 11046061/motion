CREATE DATABASE `healthy`;
USE `healthy`;

CREATE TABLE `members` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    age INT
);

INSERT INTO `members`(username, password, email, birthdate) VALUES('李哲綸','11046067','11046067@ntub.edu.tw','2002-12-21');

ALTER TABLE `members`
    CHANGE COLUMN  `birthdate` `birthday`DATE;
SELECT * FROM `members`;





