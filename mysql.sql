CREATE DATABASE `healthy`;
USE `healthy`;

SHOW VARIABLES LIKE 'default_authentication_plugin';
SET GLOBAL default_authentication_plugin='mysql_native_password';

CREATE TABLE `members` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    age INT
);

INSERT INTO `members`(username, password, email, birthdate) VALUES('李哲綸','11046067','11046067@ntub.edu.tw','2002-12-21');

ALTER TABLE `members`
    CHANGE COLUMN  `age` `birthday`DATE;
SELECT * FROM `members`;

CREATE TABLE `questions` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    member_id INT NOT NULL,
    question TEXT not null,
    answer TEXT not null,
    asked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (member_id) REFERENCES members(id)
);

SELECT * FROM `questions`;

CREATE TABLE posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    members_id INT,
    content TEXT,
    likes INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (members_id) REFERENCES members(id)
);
SELECT * FROM `posts`;

CREATE TABLE post_images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT,
    image_path VARCHAR(255),
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
);

SELECT * FROM `post_images`;


CREATE TABLE post_videos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT,
    video_path VARCHAR(255),
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
);
SELECT * FROM `post_videos`;

# 更新後的 comments 表格創建語句
CREATE TABLE comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT,
    members_id INT,
    content TEXT,
    parent_comment_id INT DEFAULT NULL,  # 新增此字段來支持回覆功能
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id),
    FOREIGN KEY (members_id) REFERENCES members(id),
    FOREIGN KEY (parent_comment_id) REFERENCES comments(id) ON DELETE CASCADE
);
SELECT * FROM `comments`;


CREATE TABLE likes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    members_id INT,
    post_id INT,
    FOREIGN KEY (members_id) REFERENCES members(id) ON DELETE CASCADE,
    FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
);
SELECT * FROM `likes`;

CREATE TABLE comment_likes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    comment_id INT,
    members_id INT,
    FOREIGN KEY (comment_id) REFERENCES comments(id) ON DELETE CASCADE,
    FOREIGN KEY (members_id) REFERENCES members(id) ON DELETE CASCADE
);
SELECT * FROM `comment_likes`;

CREATE EVENT reset_daily_weights
ON SCHEDULE EVERY 1 DAY
STARTS '2024-10-11 00:00:00'
DO
UPDATE user_fitness_data SET weight_today = NULL WHERE weight_today IS NOT NULL;

CREATE TABLE user_fitness_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL, -- 連接 members 表中的 user_id
    height INT NOT NULL, -- 身高
    weight_today INT NOT NULL, -- 當天體重
    date DATE NOT NULL, -- 日期
    FOREIGN KEY (user_id) REFERENCES members(id) -- 與 members 表的 user_id 關聯
);

ALTER TABLE `members`
ADD COLUMN `height` DECIMAL(5,2),  -- 身高（以公分為單位，可以是小數點）
ADD COLUMN `weight` DECIMAL(5,2);  -- 體重（以公斤為單位，可以是小數點）

CREATE TABLE plans (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    date DATE NOT NULL,
    completed BOOLEAN NOT NULL,
    FOREIGN KEY (user_id) REFERENCES members(id)
);


CREATE TABLE plans_completed (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES members(id) ON DELETE CASCADE
);

DESCRIBE members;