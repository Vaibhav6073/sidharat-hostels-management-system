from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
import sqlite3
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'sidharat_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory
if not os.path.exists('uploads'):
    os.makedirs('uploads')

def get_db_connection():
    conn = sqlite3.connect('hostel.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    conn.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        room_number INTEGER,
        check_in_date TEXT,
        monthly_fee REAL DEFAULT 5000
    )''')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS rooms (
        room_number INTEGER PRIMARY KEY,
        capacity INTEGER DEFAULT 2,
        occupied INTEGER DEFAULT 0,
        floor INTEGER DEFAULT 0
    )''')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS rent_payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        month TEXT,
        year INTEGER,
        amount REAL,
        paid_date TEXT,
        FOREIGN KEY (student_id) REFERENCES students (id)
    )''')
    
    conn.execute('''CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        document_name TEXT NOT NULL,
        document_type TEXT,
        file_path TEXT,
        upload_date TEXT,
        FOREIGN KEY (student_id) REFERENCES students (id)
    )''')
    
    # Add floor column if it doesn't exist
    try:
        conn.execute('ALTER TABLE rooms ADD COLUMN floor INTEGER DEFAULT 0')
    except:
        pass
    
    # Add last_rent_paid column to students if it doesn't exist
    try:
        conn.execute('ALTER TABLE students ADD COLUMN last_rent_paid TEXT')
    except:
        pass
    
    # Add default_rent column to rooms if it doesn't exist
    try:
        conn.execute('ALTER TABLE rooms ADD COLUMN default_rent REAL DEFAULT 5000')
    except:
        pass
    
    # Initialize rooms with floor assignment
    # Ground Floor: 1-5, First Floor: 101-120, Second Floor: 201-220
    floors = [(0, range(1, 6)), (1, range(101, 121)), (2, range(201, 221))]
    
    for floor, room_range in floors:
        for room_num in room_range:
            conn.execute('INSERT OR IGNORE INTO rooms (room_number, capacity, occupied, floor) VALUES (?, 2, 0, ?)', (room_num, floor))
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students ORDER BY room_number').fetchall()
    total_students = conn.execute('SELECT COUNT(*) FROM students').fetchone()[0]
    occupied_rooms = conn.execute('SELECT COUNT(DISTINCT room_number) FROM students').fetchone()[0]
    
    # Calculate total beds and available beds dynamically
    total_beds = conn.execute('SELECT SUM(capacity) FROM rooms').fetchone()[0]
    available_beds = total_beds - total_students
    
    conn.close()
    return render_template('index.html', 
                         students=students, 
                         total_students=total_students,
                         occupied_rooms=occupied_rooms,
                         total_beds=total_beds,
                         available_beds=available_beds)

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name'].strip()
        phone = request.form['phone'].strip()
        room_number = int(request.form['room_number'])
        
        if not name or not phone:
            flash('Name and phone are required!', 'error')
            return redirect(url_for('add_student'))
        
        conn = get_db_connection()
        
        # Check if phone already exists
        existing = conn.execute('SELECT id FROM students WHERE phone = ?', (phone,)).fetchone()
        if existing:
            flash('Phone number already registered!', 'error')
            conn.close()
            return redirect(url_for('add_student'))
        
        # Check room availability
        room = conn.execute('SELECT occupied, capacity FROM rooms WHERE room_number = ?', (room_number,)).fetchone()
        
        if room and room['occupied'] < room['capacity']:
            # Get room's default rent
            room_rent = conn.execute('SELECT COALESCE(default_rent, 5000) FROM rooms WHERE room_number = ?', (room_number,)).fetchone()[0]
            
            conn.execute('''INSERT INTO students (name, phone, room_number, check_in_date, monthly_fee)
                           VALUES (?, ?, ?, ?, ?)''', 
                        (name, phone, room_number, datetime.now().strftime('%Y-%m-%d'), room_rent))
            
            conn.execute('UPDATE rooms SET occupied = occupied + 1 WHERE room_number = ?', (room_number,))
            conn.commit()
            flash(f'Student {name} added successfully to Room {room_number}!', 'success')
        else:
            flash('Room is full or does not exist!', 'error')
        
        conn.close()
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    
    # Get available rooms grouped by floor
    floors_data = {}
    floor_names = {0: 'Ground Floor', 1: 'First Floor', 2: 'Second Floor'}
    
    for floor_num in [0, 1, 2]:
        rooms = conn.execute('''SELECT room_number, occupied, capacity, floor
                               FROM rooms WHERE occupied < capacity AND floor = ?
                               ORDER BY room_number''', (floor_num,)).fetchall()
        if rooms:
            floors_data[floor_num] = {
                'name': floor_names[floor_num],
                'rooms': rooms
            }
    
    conn.close()
    return render_template('add_student.html', floors_data=floors_data)

@app.route('/remove_student/<int:student_id>')
def remove_student(student_id):
    conn = get_db_connection()
    
    student = conn.execute('SELECT name, room_number FROM students WHERE id = ?', (student_id,)).fetchone()
    
    if student:
        conn.execute('DELETE FROM students WHERE id = ?', (student_id,))
        conn.execute('UPDATE rooms SET occupied = occupied - 1 WHERE room_number = ?', (student['room_number'],))
        conn.commit()
        flash(f'Student {student["name"]} removed successfully!', 'success')
    else:
        flash('Student not found!', 'error')
    
    conn.close()
    return redirect(url_for('index'))

@app.route('/rooms')
def rooms():
    conn = get_db_connection()
    
    # Get rooms grouped by floor
    floors_data = {}
    floor_names = {0: 'Ground Floor', 1: 'First Floor', 2: 'Second Floor'}
    
    for floor_num in [0, 1, 2]:
        rooms = conn.execute('''SELECT r.room_number, r.capacity, r.occupied, r.floor,
                               GROUP_CONCAT(s.name) as students,
                               COALESCE(AVG(s.monthly_fee), COALESCE(r.default_rent, 5000)) as room_rent
                               FROM rooms r
                               LEFT JOIN students s ON r.room_number = s.room_number
                               WHERE r.floor = ?
                               GROUP BY r.room_number
                               ORDER BY r.room_number''', (floor_num,)).fetchall()
        floors_data[floor_num] = {
            'name': floor_names[floor_num],
            'rooms': rooms
        }
    
    conn.close()
    return render_template('rooms.html', floors_data=floors_data)

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    students = conn.execute('''SELECT * FROM students 
                              WHERE name LIKE ? OR phone LIKE ? OR room_number = ?
                              ORDER BY name''', 
                           (f'%{query}%', f'%{query}%', query if query.isdigit() else -1)).fetchall()
    conn.close()
    
    return render_template('search_results.html', students=students, query=query)

@app.route('/update_capacity/<int:room_number>', methods=['POST'])
def update_capacity(room_number):
    new_capacity = int(request.form['capacity'])
    
    if new_capacity < 1 or new_capacity > 10:
        flash('Capacity must be between 1 and 10!', 'error')
        return redirect(url_for('rooms'))
    
    conn = get_db_connection()
    
    # Check current occupancy
    room = conn.execute('SELECT occupied FROM rooms WHERE room_number = ?', (room_number,)).fetchone()
    
    if room and new_capacity < room['occupied']:
        flash(f'Cannot reduce capacity below current occupancy ({room["occupied"]})!', 'error')
    else:
        conn.execute('UPDATE rooms SET capacity = ? WHERE room_number = ?', (new_capacity, room_number))
        conn.commit()
        flash(f'Room {room_number} capacity updated to {new_capacity}!', 'success')
    
    conn.close()
    return redirect(url_for('rooms'))

@app.route('/update_rent/<int:room_number>', methods=['POST'])
def update_rent(room_number):
    new_rent = float(request.form['rent'])
    
    if new_rent < 0 or new_rent > 50000:
        flash('Rent must be between ₹0 and ₹50,000!', 'error')
        return redirect(url_for('rooms'))
    
    conn = get_db_connection()
    
    # Always update room default rent
    conn.execute('UPDATE rooms SET default_rent = ? WHERE room_number = ?', (new_rent, room_number))
    
    # Update rent for all current students in this room
    students_count = conn.execute('SELECT COUNT(*) FROM students WHERE room_number = ?', (room_number,)).fetchone()[0]
    
    if students_count > 0:
        conn.execute('UPDATE students SET monthly_fee = ? WHERE room_number = ?', (new_rent, room_number))
        
        # Update future rent payments for current month onwards
        current_date = datetime.now()
        current_month = current_date.strftime('%B')
        current_year = current_date.year
        
        # Update any unpaid rent records for current and future months
        conn.execute('''UPDATE rent_payments SET amount = ? 
                       WHERE student_id IN (SELECT id FROM students WHERE room_number = ?)
                       AND ((year = ? AND month >= ?) OR year > ?)''', 
                    (new_rent, room_number, current_year, current_month, current_year))
    
    conn.commit()
    
    if students_count > 0:
        flash(f'Room {room_number} rent updated to ₹{new_rent} for {students_count} student(s) and all future records!', 'success')
    else:
        flash(f'Room {room_number} default rent set to ₹{new_rent} for future students!', 'success')
    
    conn.close()
    return redirect(url_for('rooms'))

@app.route('/add_room', methods=['POST'])
def add_room():
    floor = int(request.form['floor'])
    room_number = int(request.form['room_number'])
    capacity = int(request.form.get('capacity', 2))
    
    conn = get_db_connection()
    
    # Check if room already exists
    existing = conn.execute('SELECT room_number FROM rooms WHERE room_number = ?', (room_number,)).fetchone()
    if existing:
        flash(f'Room {room_number} already exists!', 'error')
    else:
        conn.execute('INSERT INTO rooms (room_number, capacity, occupied, floor) VALUES (?, ?, 0, ?)', 
                    (room_number, capacity, floor))
        conn.commit()
        flash(f'Room {room_number} added to floor {floor}!', 'success')
    
    conn.close()
    return redirect(url_for('rooms'))

@app.route('/remove_room/<int:room_number>')
def remove_room(room_number):
    conn = get_db_connection()
    
    # Check if room has students
    students = conn.execute('SELECT COUNT(*) FROM students WHERE room_number = ?', (room_number,)).fetchone()[0]
    
    if students > 0:
        flash(f'Cannot remove room {room_number} - it has {students} student(s)!', 'error')
    else:
        conn.execute('DELETE FROM rooms WHERE room_number = ?', (room_number,))
        conn.commit()
        flash(f'Room {room_number} removed successfully!', 'success')
    
    conn.close()
    return redirect(url_for('rooms'))

@app.route('/rents')
def rents():
    conn = get_db_connection()
    
    # Get selected month/year from query params or use current
    selected_month = request.args.get('month')
    selected_year = request.args.get('year', type=int)
    
    current_date = datetime.now()
    if not selected_month or not selected_year:
        selected_month = current_date.strftime('%B')
        selected_year = current_date.year
    
    # Get all students with their rent status for selected month
    students = conn.execute('''SELECT s.id, s.name, s.room_number, s.monthly_fee, s.last_rent_paid,
                              CASE WHEN rp.paid_date IS NOT NULL THEN 1 ELSE 0 END as paid_this_month
                              FROM students s
                              LEFT JOIN rent_payments rp ON s.id = rp.student_id 
                                   AND rp.month = ? AND rp.year = ?
                              ORDER BY s.room_number''', 
                           (selected_month, selected_year)).fetchall()
    
    # Calculate totals
    total_rent = sum(student['monthly_fee'] for student in students)
    paid_rent = sum(student['monthly_fee'] for student in students if student['paid_this_month'])
    pending_rent = total_rent - paid_rent
    
    # Generate month/year options
    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']
    years = list(range(2020, current_date.year + 2))
    
    conn.close()
    return render_template('rents.html', 
                         students=students, 
                         selected_month=selected_month,
                         selected_year=selected_year,
                         total_rent=total_rent,
                         paid_rent=paid_rent,
                         pending_rent=pending_rent,
                         months=months,
                         years=years)

@app.route('/mark_rent_paid/<int:student_id>')
def mark_rent_paid(student_id):
    conn = get_db_connection()
    
    # Get selected month/year from form or use current
    selected_month = request.args.get('month')
    selected_year = request.args.get('year', type=int)
    
    current_date = datetime.now()
    if not selected_month or not selected_year:
        selected_month = current_date.strftime('%B')
        selected_year = current_date.year
    
    today = current_date.strftime('%Y-%m-%d')
    
    # Get student info
    student = conn.execute('SELECT name, monthly_fee FROM students WHERE id = ?', (student_id,)).fetchone()
    
    if student:
        # Check if already paid for selected month
        existing = conn.execute('SELECT id FROM rent_payments WHERE student_id = ? AND month = ? AND year = ?',
                               (student_id, selected_month, selected_year)).fetchone()
        
        if not existing:
            # Record payment
            conn.execute('''INSERT INTO rent_payments (student_id, month, year, amount, paid_date)
                           VALUES (?, ?, ?, ?, ?)''',
                        (student_id, selected_month, selected_year, student['monthly_fee'], today))
            
            # Update last rent paid date
            conn.execute('UPDATE students SET last_rent_paid = ? WHERE id = ?', (today, student_id))
            
            conn.commit()
            flash(f'Rent marked as paid for {student["name"]} - {selected_month} {selected_year}!', 'success')
        else:
            flash('Rent already paid for this month!', 'error')
    
    conn.close()
    return redirect(url_for('rents', month=selected_month, year=selected_year))

@app.route('/documents')
def documents():
    conn = get_db_connection()
    
    # Get all students with their documents
    students = conn.execute('''SELECT s.id, s.name, s.room_number, s.phone,
                              COUNT(d.id) as doc_count
                              FROM students s
                              LEFT JOIN documents d ON s.id = d.student_id
                              GROUP BY s.id
                              ORDER BY s.name''').fetchall()
    
    conn.close()
    return render_template('documents.html', students=students)

@app.route('/student_documents/<int:student_id>')
def student_documents(student_id):
    conn = get_db_connection()
    
    student = conn.execute('SELECT name, room_number FROM students WHERE id = ?', (student_id,)).fetchone()
    documents = conn.execute('SELECT * FROM documents WHERE student_id = ? ORDER BY upload_date DESC', (student_id,)).fetchall()
    
    conn.close()
    return render_template('student_documents.html', student=student, documents=documents, student_id=student_id)

@app.route('/upload_document/<int:student_id>', methods=['POST'])
def upload_document(student_id):
    if 'file' not in request.files:
        flash('No file selected!', 'error')
        return redirect(url_for('student_documents', student_id=student_id))
    
    file = request.files['file']
    document_name = request.form['document_name'].strip()
    document_type = request.form['document_type']
    
    if file.filename == '' or not document_name:
        flash('Please select a file and enter document name!', 'error')
        return redirect(url_for('student_documents', student_id=student_id))
    
    if file:
        filename = secure_filename(f"{student_id}_{document_name}_{file.filename}")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        conn = get_db_connection()
        conn.execute('''INSERT INTO documents (student_id, document_name, document_type, file_path, upload_date)
                       VALUES (?, ?, ?, ?, ?)''',
                    (student_id, document_name, document_type, file_path, datetime.now().strftime('%Y-%m-%d')))
        conn.commit()
        conn.close()
        
        flash(f'Document "{document_name}" uploaded successfully!', 'success')
    
    return redirect(url_for('student_documents', student_id=student_id))

@app.route('/download_document/<int:doc_id>')
def download_document(doc_id):
    conn = get_db_connection()
    document = conn.execute('SELECT file_path, document_name FROM documents WHERE id = ?', (doc_id,)).fetchone()
    conn.close()
    
    if document and os.path.exists(document['file_path']):
        return send_file(document['file_path'], as_attachment=True, download_name=document['document_name'])
    else:
        flash('Document not found!', 'error')
        return redirect(url_for('documents'))

@app.route('/delete_document/<int:doc_id>')
def delete_document(doc_id):
    conn = get_db_connection()
    document = conn.execute('SELECT file_path, student_id FROM documents WHERE id = ?', (doc_id,)).fetchone()
    
    if document:
        # Delete file from filesystem
        if os.path.exists(document['file_path']):
            os.remove(document['file_path'])
        
        # Delete from database
        conn.execute('DELETE FROM documents WHERE id = ?', (doc_id,))
        conn.commit()
        flash('Document deleted successfully!', 'success')
        
        student_id = document['student_id']
    else:
        flash('Document not found!', 'error')
        student_id = request.args.get('student_id', 1)
    
    conn.close()
    return redirect(url_for('student_documents', student_id=student_id))



if __name__ == '__main__':
    init_db()
    # Run on all interfaces for mobile access
    app.run(host='0.0.0.0', port=5000, debug=True)