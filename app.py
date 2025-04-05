from flask import Flask, jsonify, request, send_file, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from Database_connection.MongoDBConnection import _Employee_register_InsertData, _Employee_register_list, _Employee_register_delete
from Database_connection import MongoDBConnection
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
import pandas as pd
import threading
from engineio.async_drivers import eventlet
import webview

india_tz = timezone('Asia/Kolkata')

app = Flask(__name__, static_folder='build', static_url_path="")
CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")  # Initialize Socket.IO
print(f"Flask-SocketIO async_mode: {socketio.async_mode}")

# Serve React build files
@app.route("/")
def serve_react_app():
    return send_from_directory("build", "index.html")

@app.route("/<path:path>")
def serve_static_files(path):
    return send_from_directory("build", path)

# Register the Employee Details
@app.route("/api/registerEmployee", methods=['POST'])
def _register_employee_details():
    try:
        data = request.get_json()

        required_fields = ['employee_name', 'phone_number', 'employee_id', 'rfid_number', 'designation']
        for required_data in required_fields:
            if required_data not in data:
                return jsonify({'error': f'Missing Fields {required_data}'}), 400

        validation = MongoDBConnection._Employee_register_validation(data, updated_check=False)

        if validation:
            print(validation)
            return jsonify({'status': 'error', 'message': str(validation)})

        insert_data = _Employee_register_InsertData(data).strip()
        return jsonify({'status': 'completed', 'data': insert_data}), 200

    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/listEmployee', methods=['GET'])
def _list_employee():
    try:
        listEmployee = _Employee_register_list()
        return jsonify(listEmployee), 200

    except Exception as e:
        return jsonify({'error', str(e)}), 400

@app.route('/api/deleteEmployee/<employee_id>', methods=['DELETE'])
def _delete_employee(employee_id):
    try:
        DeletedEmployee = _Employee_register_delete(employee_id)
        return jsonify(DeletedEmployee), 200

    except Exception as e:
        return jsonify({'error', str(e)}), 400

@app.route('/api/updateEmployee', methods=['PUT'])
def _update_employee():
    try:
        data = request.get_json()


        required_fields = ['employee_name', 'phone_number', 'employee_id', 'rfid_number', 'designation']
        for required_data in required_fields:
            if required_data not in data:
                return jsonify({'error': f'Missing Fields {required_data}'}), 400



        validation = MongoDBConnection._Employee_register_validation(data, updated_check=True)
        print(validation)

        if validation:
            print(validation)
            return jsonify({'status': 'error', 'message': str(validation)})



        updated_filter = {'employee_id': data['employee_id']}
        updated_data = {'$set' : {
            'employee_name': data['employee_name'],
            'phone_number': data['phone_number'],
            'rfid_number': data['rfid_number'],
            'mail_id': data['mail_id'],
            'designation': data['designation'],
            'work_type': data['work_type']
        }}

        insert_data = MongoDBConnection._Employee_register_update(updated_filter, updated_data)
        return jsonify({'status': 'completed', 'data': insert_data}), 200

    except Exception as e:
        return jsonify({'error': str(e)})

# Attendance Dashboard
@socketio.on('get_attendance_dashboard')
def _attendance_dashboard():
    try:
        data = MongoDBConnection._Employee_attendance_deashboard()
        emit('attendance_dashboard_data', data  )
    except Exception as e:
        emit('error', {'error': str(e)})


@socketio.on('get_attendance_dashboard_user')
def _attendance_dashboard(data):
    try:
        employee_id = data.get('employee_id')
        PresentMonuth = MongoDBConnection._Employee_attendance_deashboard_user(employee_id)
        emit('attendance_dashboard_data_user', PresentMonuth  )
    except Exception as e:
        emit('error', {'error': str(e)})

# Attendance Tracking Data
# @app.route("/attendance_tracking/<rfid_number>", methods=['GET'])
# def _attendance_tracking(rfid_number):
#     try:
#         data = rfid_number
#         if not data:
#             return jsonify({'Error': "Missing Rfid"})
#
#         result = MongoDBConnection._Employee_attendance(rfid_number)
#
#         return jsonify(result)
#     except Exception as e:
#         return jsonify({'error': str(e)})

@app.route("/api/attendance_tracking/<rfid_number>", methods=['GET'])
def _attendance_tracking(rfid_number):
    try:
        if not rfid_number:
            return jsonify({'Error': "Missing RFID"})

        result = MongoDBConnection._Employee_attendance(rfid_number)

        # Emit updated attendance data to all connected clients
        AttendanceEmployee = MongoDBConnection._Employee_Attendance_data()
        socketio.emit('attendance_tracking_show_data', AttendanceEmployee)

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route("/api/attendance_tracking/employee/<employee_id>", methods=['GET'])
def _attendance_tracking_employee_id(employee_id):
    try:
        if not employee_id:
            return jsonify({'Error': "Missing RFID"})

        result = MongoDBConnection._Employee_attendance_Employee_id(employee_id)
        print(result)

        # Emit updated attendance data to all connected clients
        AttendanceEmployee = MongoDBConnection._Employee_Attendance_data_user(employee_id)
        socketio.emit('attendance_tracking_show_data_user', AttendanceEmployee)

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)})


# Attendance Tracking Data show frontend
@socketio.on('get_attendance_tracking_show')
def _attendance_tracking_show():
    try:
        AttendanceEmployee = MongoDBConnection._Employee_Attendance_data()
        emit('attendance_tracking_show_data', AttendanceEmployee, broadcast=True)
    except Exception as e:
        emit('error', {'error': str(e)})


@socketio.on('get_attendance_tracking_show_user')
def _attendance_tracking_show_user(data):
    try:
        employee_id = data.get('employee_id')
        AttendanceEmployee = MongoDBConnection._Employee_Attendance_data_user(employee_id)
        emit('attendance_tracking_show_data_user', AttendanceEmployee, broadcast=True)
    except Exception as e:
        emit('error', {'error': str(e)})

# Search the Filter Attendance Reports
@app.route("/api/search_the_filter_attendance_reports", methods=['POST'])
def _search_the_filter_attendance_reports():
    try:
        data  = request.get_json()

        result_filter = MongoDBConnection._Search_the_filter_attendance(data)
        return jsonify(result_filter)
    except Exception as e:
        return {'error': str(e)}


@app.route("/api/search_the_filter_attendance_reports_user", methods=['POST'])
def _search_the_filter_attendance_reports_user():
    try:
        data  = request.get_json()
        print(data)
        result_filter = MongoDBConnection._Search_the_filter_attendance_user(data)
        return jsonify(result_filter)
    except Exception as e:
        return {'error': str(e)}


# Login API Endpoint
@app.route('/api/login', methods=['POST'])
def login():
    try:
        # Get JSON data from the request
        data = request.get_json()
        username = data.get('email_id').strip()
        password = data.get('password').strip()

        # Check if username and password are provided
        if not username or not password:
            return jsonify({"status": "error", "message": "Username and password are required"}), 400

        login_access = MongoDBConnection._Login_user(data)

        return jsonify(login_access), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/user/login', methods=['POST'])
def userlogin():
    try:
        data = request.get_json()
        username = data.get('email_id')
        password = data.get('password')

        print(username, password)

        # Check if username and password are provided
        if not username or not password:
            return jsonify({"status": "error", "message": "Username and password are required"}), 400

        login_access = MongoDBConnection._User_login(data)

        return jsonify(login_access), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500




@socketio.on('get_user_present_date')
def _check_user_present_based_on(data):
    try:
        employee_id = data.get('employee_id')
        CheckPresent = MongoDBConnection._Check_present_on_attendance(employee_id)
        emit('user_present_date', CheckPresent, broadcast=True)
    except Exception as e:
        emit('error', {'error': str(e)})


@app.route('/api/download', methods=['POST'])
def _download_the_filter_attendance_reports():
    try:
        data  = request.get_json()
        result_filter = MongoDBConnection._Download_attendance_reports(data)
        df = pd.DataFrame(result_filter)
        print(df)
        file_path = "attendance_data.xlsx"
        df.to_excel(file_path, index=False)

        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return {'error': str(e)}



@app.route('/api/chart_data', methods=['GET'])
def _Chart_data_for_admin():
    try:
        chart_data = MongoDBConnection._Chart_data_admin()
        return jsonify(chart_data), 200
    except Exception as e:
        return {'error': str(e)}


# 🔹 Initialize APScheduler
scheduler = BackgroundScheduler()
scheduler.add_job(MongoDBConnection._Mark_absent_on_attendance, 'cron', hour=23, minute=00, timezone=india_tz)  # Run daily at 11:59 PM
scheduler.start()

def run_application():
    socketio.run(app, use_reloader=False)

if __name__ == "__main__":
    # threading.Thread(target=run_application, daemon=True).start()
    socketio.run(app, allow_unsafe_werkzeug=True, debug=True, host="0.0.0.0")
    # webview.create_window("Attendance Managements System", "http://127.0.0.1:5000", maximized=True)
    # webview.start()
