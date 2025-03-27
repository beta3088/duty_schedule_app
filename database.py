import mysql.connector
from datetime import date

DATABASE_CONFIG = {
    'host': '127.0.0.1',  # 替换为您的 MySQL 主机名或 IP 地址
    'user': 'root',  # 替换为您的 MySQL 用户名
    'password': 'your_password',  # 替换为您的 MySQL 密码
    'database': 'duty_schedule',  # 替换为您希望使用的数据库名
    'raise_on_warnings': True
}

def get_db():
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

def init_db():
    conn = get_db()
    if conn:
        cursor = conn.cursor()
        try:
            with open('schema.sql', 'r') as f:
                sql_statements = f.read().split(';')
                for statement in sql_statements:
                    statement = statement.strip()
                    if statement:
                        cursor.execute(statement)
            conn.commit()
            print("MySQL database initialized.")
        except mysql.connector.Error as err:
            print(f"Error initializing MySQL database: {err}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()
    else:
        print("Failed to connect to MySQL, cannot initialize database.")

def query_db(query, args=(), one=False):
    conn = get_db()
    if conn:
        cursor = conn.cursor(dictionary=True)  # 使用 dictionary=True
        try:
            cursor.execute(query, args)
            rv = cursor.fetchall()
            return (rv[0] if rv else None) if one else rv
        except mysql.connector.Error as err:
            print(f"Error querying MySQL database: {err}")
            return None
        finally:
            cursor.close()
            conn.close()
    return None

def execute_db(query, args=()):
    conn = get_db()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute(query, args)
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Error executing MySQL database command: {err}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

def get_all_staff():
    """获取所有员工信息。"""
    return query_db('SELECT id, name, status FROM staff')

def get_valid_staff():
    """获取所有状态为“有效”的员工信息。"""
    return query_db('SELECT id, name FROM staff WHERE status = %s', ('有效',))

def get_staff_by_name(name):
    """根据姓名获取员工信息。"""
    return query_db('SELECT id, name, status FROM staff WHERE name = %s', (name,), one=True)

def add_staff(name):
    """添加新员工，状态默认为“有效”。"""
    try:
        execute_db('INSERT INTO staff (name, status) VALUES (%s, %s)', (name, '有效'))
        return True
    except mysql.connector.Error as err:
        print(f"Error adding staff: {err}")
        return False

def update_staff_status(staff_id, status):
    """更新员工状态。"""
    execute_db('UPDATE staff SET status = %s WHERE id = %s', (status, staff_id))

if __name__ == '__main__':
    init_db()