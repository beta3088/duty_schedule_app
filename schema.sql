DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user'
);

DROP TABLE IF EXISTS staff;
CREATE TABLE staff (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT '有效'
);

DROP TABLE IF EXISTS schedule;
CREATE TABLE schedule (
    id INT PRIMARY KEY AUTO_INCREMENT,
    date DATE UNIQUE NOT NULL,
    staff_id INT,
    FOREIGN KEY (staff_id) REFERENCES staff(id)
);

DROP TABLE IF EXISTS holidays;
CREATE TABLE holidays (
    date DATE UNIQUE NOT NULL,
    is_workday BOOLEAN NOT NULL
);

-- 初始化管理员和普通用户 (测试环境，密码明文)
INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin');
INSERT INTO users (username, password, role) VALUES ('user', 'user123', 'user');

-- 示例 staff 数据
INSERT INTO staff (name, status) VALUES ('张三', '有效');
INSERT INTO staff (name, status) VALUES ('李四', '有效');
INSERT INTO staff (name, status) VALUES ('王五', '有效');
INSERT INTO staff (name, status) VALUES ('赵六', '有效');
INSERT INTO staff (name, status) VALUES ('莫', '有效');

-- 示例 holidays 数据 (根据您的文档)
INSERT INTO holidays (date, is_workday) VALUES
('2025-01-01', FALSE), ('2025-01-28', FALSE), ('2025-01-29', FALSE), ('2025-01-30', FALSE),
('2025-01-31', FALSE), ('2025-02-08', TRUE), ('2025-04-04', FALSE), ('2025-05-01', FALSE),
('2025-05-02', FALSE), ('2025-05-31', FALSE), ('2025-09-27', FALSE), ('2025-10-01', FALSE),
('2025-10-02', FALSE), ('2025-10-03', FALSE);