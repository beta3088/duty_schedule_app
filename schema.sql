DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user'
);

DROP TABLE IF EXISTS staff;
CREATE TABLE staff (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL DEFAULT '有效'
);

DROP TABLE IF EXISTS schedule;
CREATE TABLE schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT UNIQUE NOT NULL,
    staff_id INTEGER,
    FOREIGN KEY (staff_id) REFERENCES staff(id)
);

DROP TABLE IF EXISTS holidays;
CREATE TABLE holidays (
    date TEXT UNIQUE NOT NULL,
    is_workday INTEGER NOT NULL
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
('2025-01-01', 0), ('2025-01-28', 0), ('2025-01-29', 0), ('2025-01-30', 0),
('2025-01-31', 0), ('2025-02-08', 1), ('2025-04-04', 0), ('2025-05-01', 0),
('2025-05-02', 0), ('2025-05-31', 0), ('2025-09-27', 0), ('2025-10-01', 0),
('2025-10-02', 0), ('2025-10-03', 0);