-- 好友
CREATE TABLE Friendships (
    FriendshipID INT AUTO_INCREMENT,
    mb_id1 INT NOT NULL,
    mb_id2 INT NOT NULL,
    Status VARCHAR(10) NOT NULL DEFAULT 'pending',
    StartDate DATE NOT NULL,
    PRIMARY KEY (FriendshipID),
    FOREIGN KEY (mb_id1) REFERENCES members(mb_id),
    FOREIGN KEY (mb_id2) REFERENCES members(mb_id)
);

-- 貼文
CREATE TABLE Posts (
    post_id INT AUTO_INCREMENT,
    mb_id INT NOT NULL,
    Content TEXT NOT NULL,
    Timestamp DATETIME NOT NULL,
    Location VARCHAR(255),
    ImageURL VARCHAR(255),
    PRIMARY KEY (post_id),
    FOREIGN KEY (mb_id) REFERENCES members(mb_id)
);

-- 留言
CREATE TABLE Comments (
    CommentID INT AUTO_INCREMENT,
    post_id INT NOT NULL,
    mb_id INT NOT NULL,
    Content TEXT NOT NULL,
    Timestamp DATETIME NOT NULL,
    PRIMARY KEY (CommentID),
    FOREIGN KEY (post_id) REFERENCES Posts(post_id),
    FOREIGN KEY (mb_id) REFERENCES members(mb_id)
);

-- 按讚
CREATE TABLE Likes (
    LikeID INT AUTO_INCREMENT,
    post_id INT NOT NULL,
    mb_id INT NOT NULL,
    Timestamp DATETIME NOT NULL,
    PRIMARY KEY (LikeID),
    FOREIGN KEY (post_id) REFERENCES Posts(post_id),
    FOREIGN KEY (mb_id) REFERENCES members(mb_id)
);