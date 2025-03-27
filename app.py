from flask import Flask, render_template, request, redirect, url_for, session
from datetime import date, timedelta
from database import get_db, query_db, execute_db, get_valid_staff, get_staff_by_name, add_staff, update_staff_status, get_all_staff
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于 session 加密，请务必更改

def login_required(role=None):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            if not session.get('user_id'):
                return redirect(url_for('login'))
            if role and session.get('user_role') != role:
                return render_template('error.html', message='无权限访问'), 403
            return fn(*args, **kwargs)
        wrapper.__name__ = fn.__name__  # 手动设置 wrapper 函数的 __name__ 属性
        return wrapper
    return decorator

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = query_db('SELECT * FROM users WHERE username = ? AND password = ?', (username, password), one=True)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_role'] = user['role']
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='登录失败，请检查用户名或密码')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('user_role', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required()
def index():
    year = date.today().year  # 默认显示当前年份的值班表
    schedule_data = {}
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    current_date = start_date
    while current_date <= end_date:
        schedule = query_db('SELECT s.staff_id, st.name FROM schedule s JOIN staff st ON s.staff_id = st.id WHERE s.date = ?', (current_date.strftime('%Y-%m-%d'),), one=True)
        schedule_data[current_date] = schedule['name'] if schedule else None
        current_date += timedelta(days=1)

    valid_staff = get_valid_staff()
    staff_colors = {staff['name']: "#{:06x}".format(random.randint(0, 0xFFFFFF)) for staff in valid_staff}

    return render_template('index.html', schedule_data=schedule_data, year=year, staff_colors=staff_colors)

@app.route('/init_schedule_form')
@login_required(role='admin')
def init_schedule_form():
    return render_template('init_schedule.html')

@app.route('/init_schedule', methods=['POST'])
@login_required(role='admin')
def init_schedule():
    year = int(request.form['year'])
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    current_date = start_date

    # 清空指定年份的现有排班
    execute_db('DELETE FROM schedule WHERE strftime("%Y", date) = ?', (str(year),))

    valid_staff = [staff['id'] for staff in get_valid_staff()]
    if not valid_staff:
        return render_template('result.html', message='初始化失败：没有有效的员工。')

    staff_index = 0
    while current_date <= end_date:
        day_of_week = current_date.weekday()  # Monday is 0 and Sunday is 6
        holiday = query_db('SELECT is_workday FROM holidays WHERE date = ?', (current_date.strftime('%Y-%m-%d'),), one=True)

        is_holiday = holiday is not None and holiday['is_workday'] == 0
        is_weekday = 0 <= day_of_week <= 4

        if is_weekday and not is_holiday:
            staff_id = valid_staff[staff_index % len(valid_staff)]
            execute_db('INSERT INTO schedule (date, staff_id) VALUES (?, ?)', (current_date.strftime('%Y-%m-%d'), staff_id))
            staff_index += 1
            if staff_index >= len(valid_staff):
                staff_index = 0 # 循环分配

        current_date += timedelta(days=1)

    # 处理“莫”不在周一的规则 (需要先获取所有 '莫' 的 staff_id)
    mo_staff = get_staff_by_name('莫')
    if mo_staff:
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() == 0: # Monday
                schedule_on_monday = query_db('SELECT id, staff_id FROM schedule WHERE date = ?', (current_date.strftime('%Y-%m-%d'),), one=True)
                if schedule_on_monday and schedule_on_monday['staff_id'] == mo_staff['id']:
                    # 找到前一天 (Sunday) 的排班
                    previous_date = current_date - timedelta(days=1)
                    schedule_on_sunday = query_db('SELECT id, staff_id FROM schedule WHERE date = ?', (previous_date.strftime('%Y-%m-%d'),), one=True)
                    if schedule_on_sunday:
                        # 交换值班人员
                        execute_db('UPDATE schedule SET staff_id = ? WHERE id = ?', (schedule_on_sunday['staff_id'], schedule_on_monday['id']))
                        execute_db('UPDATE schedule SET staff_id = ? WHERE id = ?', (mo_staff['id'], schedule_on_sunday['id']))
                        print(f"Swapped '莫' from {current_date} to {previous_date}")

            current_date += timedelta(days=1)

    return render_template('result.html', message=f'{year}年值班表初始化完成。')

@app.route('/manage_staff')
@login_required(role='admin')
def manage_staff():
    staff_list = get_all_staff()
    return render_template('manage_staff.html', staff_list=staff_list)

@app.route('/add_staff', methods=['POST'])
@login_required(role='admin')
def add_staff_route():
    name = request.form['name']
    staff = get_staff_by_name(name)
    if staff:
        update_staff_status(staff['id'], '有效')
        message = f'员工 "{name}" 状态已更新为有效。'
    else:
        if add_staff(name):
            message = f'员工 "{name}" 添加成功。'
        else:
            message = f'添加员工 "{name}" 失败，该姓名可能已存在。'
    return render_template('result.html', message=message)

@app.route('/delete_staff/<int:staff_id>', methods=['POST'])
@login_required(role='admin')
def delete_staff(staff_id):
    # 获取被删除员工的姓名
    deleted_staff = query_db('SELECT name FROM staff WHERE id = ?', (staff_id,), one=True)
    if not deleted_staff:
        return render_template('result.html', message=f'删除员工失败：找不到 ID 为 {staff_id} 的员工。')
    deleted_staff_name = deleted_staff['name']

    # 将员工状态更新为“无效”
    update_staff_status(staff_id, '无效')

    # 获取所有有效的员工 ID
    valid_staff = [staff['id'] for staff in get_valid_staff()]
    if not valid_staff:
        return render_template('result.html', message=f'员工 "{deleted_staff_name}" 已标记为无效，但无法重新分配班次，因为没有其他有效员工。')

    # 获取未来分配给被删除员工的班次
    today = date.today().strftime('%Y-%m-%d')
    future_schedule = query_db('SELECT id, date FROM schedule WHERE staff_id = ? AND date >= ?', (staff_id, today))

    # 重新分配班次
    valid_staff_index = 0
    for record in future_schedule:
        new_staff_id = valid_staff[valid_staff_index % len(valid_staff)]
        execute_db('UPDATE schedule SET staff_id = ? WHERE id = ?', (new_staff_id, record['id']))
        valid_staff_index += 1
        if valid_staff_index >= len(valid_staff):
            valid_staff_index = 0 # 循环分配

    return redirect(url_for('manage_staff'))

@app.route('/manage_staff_form')
@login_required(role='admin')
def manage_staff_form():
    return render_template('manage_staff_form.html')

@app.route('/update_schedule_form')
@login_required(role='admin')
def update_schedule_form():
    valid_staff = get_valid_staff()
    return render_template('update_schedule.html', staff_list=valid_staff)

@app.route('/update_schedule', methods=['POST'])
@login_required(role='admin')
def update_schedule():
    start_date_str = request.form['start_date']
    staff_to_add = request.form.getlist('add_staff')
    staff_to_remove_id = request.form.get('remove_staff')

    try:
        start_date = date.fromisoformat(start_date_str)
        if start_date < date.today():
            return render_template('result.html', message='开始日期不能早于当前日期。')

        if staff_to_remove_id:
            update_staff_status(staff_to_remove_id, '无效')
            # 重新分配逻辑已经在 delete_staff 中处理，这里不需要重复处理
            print(f"员工 ID {staff_to_remove_id} 已标记为无效。")

        for staff_name in staff_to_add:
            if staff_name:
                staff = get_staff_by_name(staff_name)
                if staff:
                    update_staff_status(staff['id'], '有效')
                    print(f"员工 '{staff_name}' 状态已更新为有效。")
                else:
                    add_staff(staff_name)
                    print(f"员工 '{staff_name}' 已添加。")

        return render_template('result.html', message='排班更新完成。')

    except ValueError:
        return render_template('result.html', message='无效的日期格式。')

@app.route('/swap_schedule', methods=['POST'])
@login_required(role='admin')
def swap_schedule():
    data = request.get_json()
    date1_str = data.get('date1')
    date2_str = data.get('date2')

    schedule1 = query_db('SELECT id, staff_id FROM schedule WHERE date = ?', (date1_str,), one=True)
    schedule2 = query_db('SELECT id, staff_id FROM schedule WHERE date = ?', (date2_str,), one=True)

    if schedule1 and schedule2:
        staff1 = schedule1['staff_id']
        staff2 = schedule2['staff_id']
        execute_db('UPDATE schedule SET staff_id = ? WHERE id = ?', (staff2, schedule1['id']))
        execute_db('UPDATE schedule SET staff_id = ? WHERE id = ?', (staff1, schedule2['id']))
        return {'success': True}
    else:
        return {'success': False, 'message': '无法找到指定日期的排班记录。'}

if __name__ == '__main__':
    app.run(debug=True)