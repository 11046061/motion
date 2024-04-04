create database `test`
show databases;
use `test`;

create table `members`(
	`memberID` int primary key,
    `name` varchar(50),
    `gender` enum('male','femal'),
    `age` int,
    `height`float,
    `weight` float,
    `emali`varchar(100),
    `date`date );
describe `members`;
