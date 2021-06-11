drop database if exists `ops`;
create database `ops` character set utf8 collate utf8_general_ci;

insert into tb_editors
(id, username, email, password)