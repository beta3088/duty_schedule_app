import sqlite3
from datetime import date

DATABASE = 'schedule.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as db:
        with open('schema.sql', 'r') as f:
            db.cursor().executescript(f.read())
        print("Database initialized.")

def query_db(query, args=(), one=False):
    conn = get_db()
    cur = conn.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    conn = get_db()
    cur = conn.execute(query, args)
    conn.commit()
    cur.close()
    conn.close()

def get_all_staff():
    """获取所有员工信息。"""
    return query_db('SELECT id, name, status FROM staff')

def get_valid_staff():
    """获取所有状态为“有效”的员工信息。"""
    return query_db('SELECT id, name FROM staff WHERE status = ?', ('有效',))

def get_staff_by_name(name):
    """根据姓名获取员工信息。"""
    return query_db('SELECT id, name, status FROM staff WHERE name = ?', (name,), one=True)

def add_staff(name):
    """添加新员工，状态默认为“有效”。"""
    try:
        execute_db('INSERT INTO staff (name, status) VALUES (?, ?)', (name, '有效'))
        return True
    except sqlite3.IntegrityError:
        return False # 姓名已存在

def update_staff_status(staff_id, status):
    """更新员工状态。"""
    execute_db('UPDATE staff SET status = ? WHERE id = ?', (status, staff_id))

if __name__ == '__main__':
    init_db()