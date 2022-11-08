DROP DATABASE shopDB;
CREATE DATABASE shopDB;
USE shopDB;

CREATE TABLE Lockers (
    locker_id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    locker CHAR(2) NOT NULL,
    lot INT NOT NULL,
    occupied BOOLEAN,
    closed BOOLEAN 
);

INSERT INTO Lockers 
(locker, lot, occupied, closed) 
VALUES ("A", 1, 0, 0)

INSERT INTO Lockers 
(locker, lot, occupied, closed) 
VALUES ("A", 2, 1, 1)