from pymongo import MongoClient
from bson import ObjectId, json_util
from datetime import datetime, timedelta
import json
import uuid
import bcrypt
import pytz
import traceback

# Basic DB Configuration
# mongodb_connection = MongoClient('localhost:27017')
# mongodb_connection = MongoClient('mongodb+srv://vrvimalraj04:s1WarkceHiLQ47jh@cluster0.edetq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0', tls=True,
#     tlsAllowInvalidCertificates=True)
mongodb_connection = MongoClient('mongodb+srv://Thikseofeuse:Thikse%402025@thikseofeuse.pny74.mongodb.net/?retryWrites=true&w=majority&appName=thikseofeuse', tls=True,
    tlsAllowInvalidCertificates=True)
db = mongodb_connection['attendance']
CollectionName = db['employee_details']
AttendanceCollection = db['attendance_tracker']
LoginCollection = db['logindata']
UserLoginData = db['userlogindata']
ErrorHandling = db['errorhandling']

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


def _MongoDB_connection(mongodb_url:str):
    try:
        mongodb_connection = MongoClient(mongodb_url,  tls=True, tlsAllowInvalidCertificates=True)
        return "Successfully Connected to MongoDB"
    except Exception as e:
        return str(e)


# def _Employee_register_validation(data: dict, updated_check: bool):
#     try:
#         Employee_id = data['employee_id']
#         RFID_number = data['rfid_number']
#         Mail_id = data['mail_id']
#
#         both_check_Employee_id_and_RFID_number = CollectionName.find_one({'employee_id': Employee_id, 'rfid_number': RFID_number, 'mail_id': Mail_id})
#         check_Employee_id = CollectionName.find_one({'employee_id': Employee_id})
#         check_RFID_number = CollectionName.find_one({'rfid_number': RFID_number})
#         check_Mail_id = CollectionName.find_one({'mail_id': Mail_id})
#
#         print(check_RFID_number['rfid_number'])
#         if updated_check:
#             if check_RFID_number:
#                 if check_RFID_number['rfid_number'] == RFID_number:
#                     return False
#                 else:
#                     return "RFID Number was Already Register !...."
#             elif check_Mail_id:
#                 if check_Mail_id['mail_id'] == Mail_id:
#                     return False
#                 else:
#                     return "Mail ID are Already Register !...."
#             else:
#                 return False
#         else:
#             if both_check_Employee_id_and_RFID_number:
#                 return "employee Id,Mail ID and RFID Number are Already Register !...."
#             elif check_Employee_id:
#                 return "Employee Id was Already Register !...."
#             elif check_RFID_number:
#                 return "RFID Number was Already Register !...."
#             elif check_Mail_id:
#                 return "Mail ID are Already Register !...."
#             else:
#                 return False
#
#     except Exception as e:
#         return str(e)

def _Employee_register_validation(data: dict, updated_check: bool):
    try:
        Employee_id, RFID_number, Mail_id = data['employee_id'], data['rfid_number'], data['mail_id']

        existing_record = CollectionName.find_one({'$or': [
            {'employee_id': Employee_id},
            {'rfid_number': RFID_number},
            {'mail_id': Mail_id}
        ]})

        if existing_record:
            print(RFID_number, '-', existing_record.get('rfid_number'))
            print(existing_record.get('rfid_number') == RFID_number)
            if updated_check:
                existing_record_updated = CollectionName.find_one({'$or': [
                    {'employee_id': Employee_id},
                    {'rfid_number': RFID_number},
                    {'mail_id': Mail_id}
                ], 'employee_id': Employee_id})
                if existing_record_updated.get('rfid_number') == RFID_number:
                    return False
                elif CollectionName.find_one({'rfid_number': RFID_number}):
                    return "RFID Number was Already Registered!..."
                else:
                    return False

                if existing_record_updated.get('mail_id') == Mail_id:
                    return False
                elif CollectionName.find_one({'mail_id': Mail_id}):
                    return "Mail ID is Already Registered!..."
                else:
                    return False

            else:
                if (
                        existing_record.get('employee_id') == Employee_id and
                        existing_record.get('rfid_number') == RFID_number and
                        existing_record.get('mail_id') == Mail_id
                ):
                    return "Employee ID, Mail ID, and RFID Number are Already Registered!..."
                if existing_record.get('employee_id') == Employee_id:
                    return "Employee ID is Already Registered!..."
                if existing_record.get('rfid_number') == RFID_number:
                    return "RFID Number is Already Registered!..."
                if existing_record.get('mail_id') == Mail_id:
                    return "Mail ID is Already Registered!..."

        return False  # No conflicts found

    except Exception as e:
        return str(e)


def _Employee_register_InsertData(data: dict):
    try:
        if len(data) == 1:
            result = CollectionName.insert_one(data)
            print("line 119", data)
            return f"Successfully Inserted a Data {result.inserted_id}"
        else:
            result = CollectionName.insert_many([data])
            username = data['mail_id']
            password = data['phone_number']
            employee_name = data['employee_name'].strip()
            employee_id = data['employee_id'].strip()
            hashed_password = hash_password(password)
            UserLoginData.insert_one({"username": username, "password": hashed_password, "employee_name": employee_name, "employee_id": employee_id})
            return f"Successfully Inserted a Data {result.inserted_ids}"

    except Exception as e:
        return str(e)


def _Employee_register_list():
    try:
        employee_list = CollectionName.find()
        return json.loads(json_util.dumps(employee_list))

    except Exception as e:
        return str(e)


def _Employee_register_delete(delete_items: str):
    try:
        result = CollectionName.delete_one({'employee_id': delete_items})
        user_login_deleted = UserLoginData.delete_one({'employee_id': delete_items})
        if result.deleted_count and user_login_deleted.deleted_count == 1:
            return {"message": "Employee Data was Deleted!"}  # Return JSON response
        else:
            return {"error": "Employee ID not found"}

    except Exception as e:
        return {"error": str(e)}

def _Employee_register_update(find_filter: dict, updated_data: dict):
    try:
        result = CollectionName.update_one(find_filter, updated_data)
        data = {'$set' : {
  "username": updated_data["$set"]['mail_id'],
  "password": hash_password(updated_data["$set"]['phone_number']),
  "employee_name": updated_data["$set"]['employee_name'],
}}
        user_login_data_updated = UserLoginData.update_one(find_filter, data)
        if result.modified_count and user_login_data_updated.modified_count == 1:
            return {f"message": "Employee Data was Updated {result.modified_count}"}  # Return JSON response
        else:
            return {"error": "Employee ID not found"}

    except Exception as e:
        return {"error": str(e)}



def _Employee_attendance(rfid_number: str):
    try:
	# Define IST timezone
        ist_timezone = pytz.timezone('Asia/Kolkata')
        date_data = datetime.now(ist_timezone)
        date = date_data.strftime('%d-%m-%Y')
        current_time = date_data.strftime('%I:%M:%S %p')

        # Check if RFID exists
        rfid_data = CollectionName.find_one({'rfid_number': rfid_number})
        if not rfid_data:
            return {'status': 'error', 'message': 'Not a valid user'}

        if rfid_data.get('work_type') == 'part_time':
                attendance_data = {
                    'Date': date,
                    'Employee_Name': rfid_data['employee_name'],
                    'Employee_id': rfid_data['employee_id'],
                    'Logged_in': current_time,
                    'Logged_out': '',
                    'total_work_hrs': '',
                    'status': 'Present',
                    'rfid_number': rfid_number,
                    'Remarks': '',
                    'Late_minutes': "",
                    'Late_hh_mm': "",
                    'Half_day': ''
                }
        else:
                # Extract hour and minute, ensuring AM-only check
                login_hour = date_data.hour
                login_minute = date_data.minute
                remarks = "Normal login"
                late_minutes = 0
                half_day = False
                late_hours = 0
                late_mins = 0


                # Apply conditions only if login is before 6 PM
                if login_hour < 18:
                    if login_hour == 9 and login_minute >= 1:
                        remarks = "Late login"
                        late_minutes = (login_hour - 8) * 60 + login_minute
                    elif login_hour >= 10:
                        remarks = "Half-day permission required"
                        late_minutes = (login_hour - 8) * 60 + login_minute
                        half_day = True

                    # Convert late minutes to hours and minutes
                    late_hours = late_minutes // 60
                    late_mins = late_minutes % 60

                # Prepare attendance data
                attendance_data = {
                    'Date': date,
                    'Employee_Name': rfid_data['employee_name'],
                    'Employee_id': rfid_data['employee_id'],
                    'Logged_in': current_time,
                    'Logged_out': '',
                    'total_work_hrs': '',
                    'status': 'Present',
                    'rfid_number': rfid_number,
                    'Remarks': remarks,
                    'Late_minutes': late_minutes,
                    'Late_hh_mm': f"{late_hours} hr {late_mins} min",
                    'Half_day': half_day
                }

        # # Prepare attendance data
        # attendance_data = {
        #     'Date': date,
        #     'Employee_Name': rfid_data['employee_name'],
        #     'Employee_id': rfid_data['employee_id'],
        #     'Logged_in': current_time,
        #     'Logged_out': '',
        #     'total_work_hrs': '',
        #     'status': 'Present',
        #     'rfid_number': rfid_number
        # }

        # Check existing attendance for the day
        existing_record = AttendanceCollection.find_one({'Date': date, 'rfid_number': rfid_number})

        if existing_record and existing_record['Logged_out']:
            return {'status': 'error', 'message': 'Already logged out for today'}

        if existing_record:
            date = date_data.strftime('%d-%m-%Y')
            current_time = date_data.strftime('%I:%M:%S %p')
            # Logout logic
            logged_in_time = existing_record['Logged_in']
            logged_out_time = current_time
            record_date = existing_record['Date']

            # Parse times (consistent date format)
            time_format = "%d-%m-%Y %I:%M:%S %p"
            logged_in = datetime.strptime(f"{record_date} {logged_in_time}", time_format)
            logged_out = datetime.strptime(f"{record_date} {logged_out_time}", time_format)

            # Calculate time difference
            time_diff = logged_out - logged_in
            total_seconds = time_diff.total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            total_work_hrs = f"{hours}:{minutes:02d} Hrs"  # Pad minutes with leading zero

            status = "Absent" if total_seconds < 1800 else "Present"

            # Update record
            # AttendanceCollection.update_one(
            #     {'Date': date, 'rfid_number': rfid_number},
            #     {'$set': {'Logged_out': current_time, 'total_work_hrs': total_work_hrs}}
            # )
            # Update record
            AttendanceCollection.update_one(
                {'Date': date, 'rfid_number': rfid_number},
                {'$set': {'Logged_out': current_time, 'total_work_hrs': total_work_hrs, 'status': status}}
            )
            return {'status': 'success', 'message': f"Successfully logged out at {current_time}.  Status: {status}"}

        # Login logic
        print(attendance_data)
        AttendanceCollection.insert_one(attendance_data)
        return {'status': 'success', 'message': f"Successfully logged in at {current_time}"}

    except Exception as e:
        return {'status': 'error', 'message': str(e)}


def _Employee_attendance_Employee_id(employee_id: str):
    try:
	# Define IST timezone
        ist_timezone = pytz.timezone('Asia/Kolkata')
        date_data = datetime.now(ist_timezone)
        date = date_data.strftime('%d-%m-%Y')
        current_time = date_data.strftime('%I:%M:%S %p')
        print(employee_id)

        # Check if RFID exists
        rfid_data = CollectionName.find_one({'employee_id': employee_id})
        if not rfid_data:
            return {'status': 'error', 'message': 'Not a valid user'}

        if rfid_data.get('work_type') == 'part_time':
                attendance_data = {
                    'Date': date,
                    'Employee_Name': rfid_data['employee_name'],
                    'Employee_id': rfid_data['employee_id'],
                    'Logged_in': current_time,
                    'Logged_out': '',
                    'total_work_hrs': '',
                    'status': 'Present',
                    'rfid_number': rfid_data.get('rfid_number'),
                    'Remarks': '',
                    'Late_minutes': "",
                    'Late_hh_mm': "",
                    'Half_day': ''
                }
        else:
                # Extract hour and minute, ensuring AM-only check
                login_hour = date_data.hour
                login_minute = date_data.minute
                remarks = "Normal login"
                late_minutes = 0
                half_day = False
                late_hours = 0
                late_mins = 0

                # Apply conditions only if login is before 6 PM
                if login_hour < 18:
                    if login_hour == 9 and login_minute >= 1:
                        remarks = "Late login"
                        late_minutes = (login_hour - 8) * 60 + login_minute
                    elif login_hour >= 10:
                        remarks = "Half-day permission required"
                        late_minutes = (login_hour - 8) * 60 + login_minute
                        half_day = True

                        # Convert late minutes to hours and minutes
                    late_hours = late_minutes // 60
                    late_mins = late_minutes % 60

                # Prepare attendance data
                attendance_data = {
                    'Date': date,
                    'Employee_Name': rfid_data['employee_name'],
                    'Employee_id': rfid_data['employee_id'],
                    'Logged_in': current_time,
                    'Logged_out': '',
                    'total_work_hrs': '',
                    'status': 'Present',
                    'rfid_number': rfid_data.get('rfid_number'),
                    'Remarks': remarks,
                    'Late_minutes': late_minutes,
                    'Late_hh_mm': f"{late_hours} hr {late_mins} min",
                    'Half_day': half_day
                }

        # # Prepare attendance data
        # attendance_data = {
        #     'Date': date,
        #     'Employee_Name': rfid_data['employee_name'],
        #     'Employee_id': rfid_data['employee_id'],
        #     'Logged_in': current_time,
        #     'Logged_out': '',
        #     'total_work_hrs': '',
        #     'status': 'Present',
        #     'rfid_number': ""
        # }

        # Check existing attendance for the day
        existing_record = AttendanceCollection.find_one({'Date': date, 'Employee_id': employee_id})

        if existing_record and existing_record['Logged_out']:
            return {'status': 'error', 'message': 'Already logged out for today'}

        if existing_record:
            date = date_data.strftime('%d-%m-%Y')
            current_time = date_data.strftime('%I:%M:%S %p')
            # Logout logic
            logged_in_time = existing_record['Logged_in']
            logged_out_time = current_time
            record_date = existing_record['Date']

            # Parse times (consistent date format)
            time_format = "%d-%m-%Y %I:%M:%S %p"
            logged_in = datetime.strptime(f"{record_date} {logged_in_time}", time_format)
            logged_out = datetime.strptime(f"{record_date} {logged_out_time}", time_format)

            # Calculate time difference
            time_diff = logged_out - logged_in
            total_seconds = time_diff.total_seconds()
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            total_work_hrs = f"{hours}:{minutes:02d} Hrs"  # Pad minutes with leading zero

            status = "Absent" if total_seconds < 1800 else "Present"

            # Update record
            # AttendanceCollection.update_one(
            #     {'Date': date, 'rfid_number': rfid_number},
            #     {'$set': {'Logged_out': current_time, 'total_work_hrs': total_work_hrs}}
            # )
            # Update record
            AttendanceCollection.update_one(
                {'Date': date, 'Employee_id': employee_id},
                {'$set': {'Logged_out': current_time, 'total_work_hrs': total_work_hrs, 'status': status}}
            )
            return {'status': 'success', 'message': f"Successfully logged out at {current_time}.  Status: {status}", "login": False}

        # Login logic
        AttendanceCollection.insert_one(attendance_data)
        return {'status': 'success', 'message': f"Successfully logged in at {current_time}", 'login': True}

    except Exception as e:
        return {'status': 'error', 'message': str(e)}



def _Employee_Attendance_data():
    try:
        employee_Attendance_data = AttendanceCollection.find()
        return json.loads(json_util.dumps(employee_Attendance_data))

    except Exception as e:
        return {'status': "error", 'message': str(e)}


def _Employee_Attendance_data_user(employee_id: str):
    try:
        employee_Attendance_data_user = AttendanceCollection.find({'Employee_id': employee_id})
        return json.loads(json_util.dumps(employee_Attendance_data_user))

    except Exception as e:
        return {'status': "error", 'message': str(e)}



def _Employee_attendance_deashboard():
    try:
        # Get today's date in the format used in your collection
        today_date = datetime.now().strftime("%d-%m-%Y")

        # Fetch attendance data for today
        attendance_data = AttendanceCollection.find({'Date': today_date})


        # Initialize counters
        total_employee_count = CollectionName.count_documents({})
        total_present_count = 0
        total_absent_count = 0
        present_employees = []

        # Iterate through attendance data
        for record in attendance_data:
            if record["Logged_in"]:  # If logged_in is not empty, the employee is present
                total_present_count += 1
                # Fetch employee details for the mini list
                # employee = CollectionName.find_one({"rfid_number": record["rfid_number"]})
                employee =  CollectionName.find_one({"$or": [
        {"rfid_number": record["rfid_number"]},
        {"employee_id": record["Employee_id"]}
    ]})
                if employee:
                    present_employees.append({
                        "employee_name": employee["employee_name"],
                        "employee_id": employee["employee_id"],
                        "work_type": employee['work_type'],
                        "time": record['Logged_in']
                    })
            else:
                total_absent_count += 1

        # Calculate absent count
        total_absent_count = total_employee_count - total_present_count

        # Prepare the response
        response = {
            "Date": today_date,
            "Total_Employee_Count": total_employee_count,
            "Total_Present_Count": total_present_count,
            "Total_Absent_Count": total_absent_count,
            "Present_Employees": present_employees
        }
        return json.loads(json_util.dumps(response))
    except Exception as e:
        return {'status': "error", 'message': str(e)}


def _Employee_attendance_deashboard_user(employee_id: str):
    try:
        # Get today's date in the format used in your collection
        current_month = datetime.now().strftime("-%m-%Y")

        # Total present across all records
        total_present_count = AttendanceCollection.count_documents({
            "Employee_id": employee_id,
            "Logged_in": {"$exists": True, "$ne": ""}
        })

        # Total absent across all records
        total_absent_count = AttendanceCollection.count_documents({
            "Employee_id": employee_id,
            "$or": [{"Logged_in": {"$exists": False}}, {"Logged_in": ""}]
        })

        # Fetch all attendance records for the current month
        monthly_attendance = list(AttendanceCollection.find({
            "Employee_id": employee_id,
            "Date": {"$regex": f".*{current_month}"}  # Match dates ending with MM-YYYY
        }))

        # Count present and absent days for the current month
        monthly_present_count = sum(1 for record in monthly_attendance if record.get("Logged_in"))
        monthly_absent_count = len(monthly_attendance) - monthly_present_count

        # Iterate through attendance data
        # Prepare attendance list
        attendance_list = [
            {
                "Date": record["Date"],
                "Logged_in": record.get("Logged_in", "N/A"),
                "Logged_out": record.get("Logged_out", "N/A"),
                "Work_Hours": record.get("total_work_hrs", "N/A"),
                "late_mins": record.get("Late_minutes", "N/A"),
                "Status": record.get('status', "")
            } for record in monthly_attendance
        ]

        # Prepare response
        response = {
            "Employee_ID": employee_id,
            "TotalPresent": total_present_count,
            "TotalAbsent": total_absent_count,
            "Current_Month_Present": monthly_present_count,
            "Current_Month_Absent": monthly_absent_count,
            "Attendance_List": attendance_list,
            "CurrentMonth": current_month
        }
        return json.loads(json_util.dumps(response))
    except Exception as e:
        return {'status': "error", 'message': str(e)}



def _Search_the_filter_attendance(filter_data):
    try:

        from_date = filter_data.get("fromDate")
        to_date = filter_data.get("toDate")
        employee_id = filter_data.get("employeeId")
        employee_name = filter_data.get("employeeName")

        # Build the query
        query = {}

	# Convert and filter by date
        if from_date:
            from_date = datetime.strptime(from_date, "%Y-%m-%d").strftime("%d-%m-%Y")
        if to_date:
            to_date = datetime.strptime(to_date, "%Y-%m-%d").strftime("%d-%m-%Y")

        # Add date range filter
        if from_date and to_date:
            query["Date"] = {"$gte": from_date, "$lte": to_date}
        elif from_date:
            query["Date"] = {"$gte": from_date}
        elif to_date:
            query["Date"] = {"$lte": to_date}

        # Add employee_id filter
        if employee_id:
            query["Employee_id"] = employee_id

        # Add employee_name filter
        if employee_name:
            query["Employee_Name"] = {"$regex": employee_name, "$options": "i"}  # Case-insensitive search


        # Fetch filtered attendance data
        attendance_data = list(AttendanceCollection.find(query, {"_id": 0}))

        # Return the response
        return json.loads(json_util.dumps(attendance_data))

    except Exception as e:
        return {'status': "error", 'message': str(e)}


def _Search_the_filter_attendance_user(filter_data):
    try:
        from_date = filter_data.get("fromDate")
        to_date = filter_data.get("toDate")
        attendanceStatus = filter_data.get("attendanceStatus")
        employee_id = filter_data.get("employeeID")

        # Build the query
        query = {}


        query['Employee_id'] = employee_id

	# Convert and filter by date
        if from_date:
            from_date = datetime.strptime(from_date, "%Y-%m-%d").strftime("%d-%m-%Y")
        if to_date:
            to_date = datetime.strptime(to_date, "%Y-%m-%d").strftime("%d-%m-%Y")

        # Add date range filter
        if from_date and to_date:
            query["Date"] = {"$gte": from_date, "$lte": to_date}
        elif from_date:
            query["Date"] = {"$gte": from_date}
        elif to_date:
            query["Date"] = {"$lte": to_date}

        if attendanceStatus:
            query['status'] = attendanceStatus

        # Case-insensitive search
        print(query)

        # Fetch filtered attendance data
        attendance_data = list(AttendanceCollection.find(query, {"_id": 0}))
        print(attendance_data)

        # Return the response
        return json.loads(json_util.dumps(attendance_data))

    except Exception as e:
        return {'status': "error", 'message': str(e)}




def _Login_user(data: dict):
    try:
        username = data.get('email_id')
        password = data.get('password')
        # Find the user in the database
        user = LoginCollection.find_one({"email_id": username})
        if not user:
            return {"status": "error", "message": "User not found"}

        # Verify the password
        if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                return {"status": "success", "message": "Login successful",
                            "user": {"username": user['username'], "email": user['email_id']}}
        else:
            return {"status": "error", "message": "Invalid password"}
    except Exception as e:
        return {'status': "error", "message": str(e)}


def _User_login(data: dict):
    try:
        username = data.get('email_id')
        password = data.get('password')
        # Find the user in the database
        user = UserLoginData.find_one({"username": username})
        if not user:
            return {"status": "error", "message": "User not found"}

        # Verify the password
        if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return {"status": "success", "message": "Login successful",
                            "user": {"employee_name": user['employee_name'], "employee_id": user['employee_id']}}
        else:
            return {"status": "error", "message": "Invalid password"}
    except Exception as e:
        return {'status': "error", "message": str(e)}



def _Mark_absent_on_attendance():
    try:
        date = datetime.now().strftime('%d-%m-%Y')

        # Fetch all employees
        all_employees = CollectionName.find({}, {"rfid_number": 1, "employee_name": 1, "employee_id": 1})

        for employee in all_employees:
            rfid_number = employee["rfid_number"]
            employee_id = employee['employee_id']

            # Check if the employee has logged in today
            # existing_attendance = AttendanceCollection.find_one({"Date": date, "rfid_number": rfid_number})

            existing_attendance = AttendanceCollection.find_one({"$or": [
        {"Date": date, "rfid_number": rfid_number},
        {"Date": date, "employee_id": employee_id}
    ]})

            if not existing_attendance:
                # Mark as absent if no login record exists
                absent_data = {
                    "Date": date,
                    "Employee_Name": employee["employee_name"],
                    "Employee_id": employee["employee_id"],
                    "Logged_in": "",
                    "Logged_out": "",
                    "total_work_hrs": "0:00 Hrs",
                    "status": "Absent",
                    "rfid_number": rfid_number,
                    'Late_minutes': 0,
                    'Late_hh_mm': f"",
                    'Half_day': False
                }
                AttendanceCollection.insert_one(absent_data)

        return {"status": "success", "message": "IAbsent employees marked successfully"}

    except Exception as e:
        return {'status': "error", "message": str(e)}

def _Check_present_on_attendance(employee_id):
    try:
        date = datetime.now().strftime('%d-%m-%Y')

        # Check if the employee has logged in today
        existing_attendance = AttendanceCollection.find_one({"Date": date, "Employee_id": employee_id})

        if existing_attendance:
            logged_in = bool(existing_attendance.get("Logged_in"))
            logged_out = bool(existing_attendance.get("Logged_out"))
            print(logged_out, logged_in)

            # If both are empty, return False
            if not logged_in and not logged_out:
                logged_in, logged_out = False, False

            return {
                "status": "success",
                "employee_id": employee_id,
                "logged_in": logged_in,
                "logged_out": logged_out
            }
        else:
            return {
                "status": "not found",
                "employee_id": employee_id,
                "logged_in": False,
                "logged_out": False
            }

    except Exception as e:
        return {'status': "error", "message": str(e)}



def _Download_attendance_reports(download_data:dict):
    try:
        from_date = download_data.get("fromDate")
        to_date = download_data.get("toDate")
        employee_id = download_data.get("employeeId")
        employee_name = download_data.get("employeeName")

        # Build the query
        query = {}

        # Convert and filter by date
        if from_date:
            from_date = datetime.strptime(from_date, "%Y-%m-%d").strftime("%d-%m-%Y")
        if to_date:
            to_date = datetime.strptime(to_date, "%Y-%m-%d").strftime("%d-%m-%Y")

        # Add date range filter
        if from_date and to_date:
            query["Date"] = {"$gte": from_date, "$lte": to_date}
        elif from_date:
            query["Date"] = {"$gte": from_date}
        elif to_date:
            query["Date"] = {"$lte": to_date}

        # Add employee_id filter
        if employee_id:
            query["Employee_id"] = employee_id

        # Add employee_name filter
        if employee_name:
            query["Employee_Name"] = {"$regex": employee_name, "$options": "i"}  # Case-insensitive search

        # Fetch filtered attendance data
        attendance_data = list(AttendanceCollection.find(query, {"_id": 0}))

        # Return the response
        return json.loads(json_util.dumps(attendance_data))

    except Exception as e:
        return {'status': "error", "message": str(e)}




def _Chart_data_admin():
    try:
        prev_date = (datetime.now() - timedelta(days=1)).strftime("%d-%m-%Y")

        # Fetch data from MongoDB for the previous date
        attendance_data = AttendanceCollection.find(
            {"Date": prev_date},  # Filter by date
            {"_id": 0, "Employee_Name": 1, "total_work_hrs": 1}  # Return only required fields
        )
        return json.loads(json_util.dumps(attendance_data))

    except Exception as e:
        # _Error_handling_(e)
        return {'status': "error", "message": str(e)}



# def _Error_handling_(e):
#     try:
#        Error_data = {
#         "error_type" : type(e).__name__ ,
#         "error_name" : e.__class__.__name__  ,
#         "error_description" : str(e)  ,
#         "error_traceback" : traceback.format_exc()
#        }
#        errorResult = ErrorHandling.insert_one(Error_data)
#     except Exception as e:
#         return str(e)








