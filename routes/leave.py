from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from db import execute_query

leave_bp = Blueprint('leave', __name__)


@leave_bp.route('/leave')
def leave_page():
    if not session.get('user_id'):
        return redirect(url_for('auth.signin'))

    role = session.get('role')
    emp_id = session.get('employee_id')

    # Get leave types for the request form
    leave_types = execute_query("SELECT id, name, max_days FROM leave_types", fetch_all=True)

    if role == 'hr_manager':
        # HR sees all pending requests
        pending = execute_query(
            """SELECT lr.id, lr.start_date, lr.end_date, lr.reason, lr.status, lr.created_at,
                      e.first_name, e.last_name, lt.name as leave_type,
                      DATEDIFF(lr.end_date, lr.start_date) + 1 as days
               FROM leave_requests lr
               JOIN employees e ON lr.employee_id = e.id
               JOIN leave_types lt ON lr.leave_type_id = lt.id
               ORDER BY FIELD(lr.status, 'Pending', 'Approved', 'Rejected'), lr.created_at DESC""",
            fetch_all=True
        )
        return render_template('leave.html',
            leave_types=leave_types or [],
            requests=pending or [],
            is_hr=True
        )
    else:
        # Employee sees own requests
        my_requests = execute_query(
            """SELECT lr.id, lr.start_date, lr.end_date, lr.reason, lr.status, lr.created_at,
                      lt.name as leave_type,
                      DATEDIFF(lr.end_date, lr.start_date) + 1 as days
               FROM leave_requests lr
               JOIN leave_types lt ON lr.leave_type_id = lt.id
               WHERE lr.employee_id = %s
               ORDER BY lr.created_at DESC""",
            (emp_id,), fetch_all=True
        )
        return render_template('leave.html',
            leave_types=leave_types or [],
            requests=my_requests or [],
            is_hr=False
        )


# ======================== API Endpoints ========================

@leave_bp.route('/api/leave/request', methods=['POST'])
def submit_leave():
    if not session.get('user_id'):
        return jsonify({'error': 'Unauthorized'}), 401

    emp_id = session.get('employee_id')
    data = request.get_json() if request.is_json else request.form

    leave_type_id = data.get('leave_type_id')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    reason = data.get('reason', '')

    if not leave_type_id or not start_date or not end_date:
        return jsonify({'error': 'All fields are required'}), 400

    if start_date > end_date:
        return jsonify({'error': 'End date must be after start date'}), 400

    result = execute_query(
        """INSERT INTO leave_requests (employee_id, leave_type_id, start_date, end_date, reason, status)
           VALUES (%s, %s, %s, %s, %s, 'Pending')""",
        (emp_id, leave_type_id, start_date, end_date, reason), commit=True
    )

    if result is None:
        return jsonify({'error': 'Failed to submit leave request'}), 500

    # Create notification for all HR managers
    hr_users = execute_query(
        "SELECT e.id as emp_id FROM employees e JOIN users u ON e.user_id = u.id WHERE u.role = 'hr_manager'",
        fetch_all=True
    )
    emp_name = f"{session.get('first_name', '')} {session.get('last_name', '')}"
    for hr in (hr_users or []):
        execute_query(
            "INSERT INTO notifications (employee_id, title, message) VALUES (%s, %s, %s)",
            (hr['emp_id'], 'New Leave Request', f'{emp_name} has submitted a leave request from {start_date} to {end_date}.'),
            commit=True
        )

    return jsonify({'success': True, 'message': 'Leave request submitted successfully', 'id': result})


@leave_bp.route('/api/leave/<int:leave_id>/approve', methods=['POST'])
def approve_leave(leave_id):
    if not session.get('user_id') or session.get('role') != 'hr_manager':
        return jsonify({'error': 'Unauthorized'}), 403

    leave_req = execute_query(
        "SELECT id, employee_id, start_date, end_date FROM leave_requests WHERE id = %s",
        (leave_id,), fetch_one=True
    )
    if not leave_req:
        return jsonify({'error': 'Leave request not found'}), 404

    execute_query(
        "UPDATE leave_requests SET status = 'Approved' WHERE id = %s",
        (leave_id,), commit=True
    )

    # Mark attendance as 'Leave' for the leave period
    import datetime
    start = leave_req['start_date']
    end = leave_req['end_date']
    curr = start
    if isinstance(curr, str):
        try:
            curr = datetime.datetime.strptime(curr, "%Y-%m-%d").date()
        except ValueError:
            curr = datetime.date.fromisoformat(curr)
    if isinstance(end, str):
        try:
            end = datetime.datetime.strptime(end, "%Y-%m-%d").date()
        except ValueError:
            end = datetime.date.fromisoformat(end)
            
    while curr <= end:
        execute_query(
            "INSERT IGNORE INTO attendance (employee_id, attendance_date, status) VALUES (%s, %s, 'Leave')",
            (leave_req['employee_id'], curr), commit=True
        )
        curr += datetime.timedelta(days=1)

    # Notify the employee
    execute_query(
        "INSERT INTO notifications (employee_id, title, message) VALUES (%s, %s, %s)",
        (leave_req['employee_id'], 'Leave Approved', f'Your leave request from {leave_req["start_date"]} to {leave_req["end_date"]} has been approved.'),
        commit=True
    )

    return jsonify({'success': True, 'message': 'Leave request approved'})


@leave_bp.route('/api/leave/<int:leave_id>/reject', methods=['POST'])
def reject_leave(leave_id):
    if not session.get('user_id') or session.get('role') != 'hr_manager':
        return jsonify({'error': 'Unauthorized'}), 403

    leave_req = execute_query(
        "SELECT id, employee_id, start_date, end_date FROM leave_requests WHERE id = %s",
        (leave_id,), fetch_one=True
    )
    if not leave_req:
        return jsonify({'error': 'Leave request not found'}), 404

    execute_query(
        "UPDATE leave_requests SET status = 'Rejected' WHERE id = %s",
        (leave_id,), commit=True
    )

    # Notify the employee
    execute_query(
        "INSERT INTO notifications (employee_id, title, message) VALUES (%s, %s, %s)",
        (leave_req['employee_id'], 'Leave Rejected', f'Your leave request from {leave_req["start_date"]} to {leave_req["end_date"]} has been rejected.'),
        commit=True
    )

    return jsonify({'success': True, 'message': 'Leave request rejected'})
