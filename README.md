# Sidharat Hostels Management System

A complete hostel management system built with Flask for managing students, rooms, rent payments, and documents.

## Features

### 🏠 Dashboard
- Real-time statistics (students, rooms, available beds)
- Student overview with room assignments
- Modern responsive UI

### 👥 Student Management
- Add/remove students with validation
- Room assignment with availability checking
- Phone number uniqueness validation
- Floor-wise room selection

### 🏨 Room Management
- Floor-wise organization (Ground, First, Second Floor)
- Dynamic capacity management (1-10 beds per room)
- Room rent management
- Add/remove rooms functionality
- Visual occupancy status

### 💰 Rent Management
- Monthly rent tracking
- Payment status (Paid/Due)
- Month/year selection for historical data
- Collection statistics and rates
- Mark payments functionality

### 📁 Document Management
- Upload student documents (ID, Educational, Medical, etc.)
- Predefined document types + custom options
- File download and deletion
- Secure file storage
- Document count tracking per student

### 🔍 Search & Navigation
- Global student search (name, phone, room)
- Clean navigation between modules
- Flash messages for user feedback

## Installation

1. **Install Python 3.11+**

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Application:**
   ```bash
   python app.py
   ```

4. **Access Application:**
   - Open browser: http://localhost:5000
   - Dashboard shows system overview

## Usage

### Adding Students
1. Go to "Add Student" 
2. Enter name and phone number
3. Select room from floor-wise dropdown
4. System assigns default room rent

### Managing Rooms
1. Go to "Rooms" tab
2. View rooms organized by floors
3. Update capacity or rent using inline forms
4. Add new rooms or remove empty ones

### Rent Tracking
1. Go to "Rents" tab
2. Select month/year to view
3. Mark students as paid
4. View collection statistics

### Document Management
1. Go to "Documents" tab
2. Select student to manage documents
3. Upload files with predefined or custom names
4. Download or delete documents as needed

## Database Structure

- **students**: Student information and rent details
- **rooms**: Room capacity, occupancy, and floor assignment
- **rent_payments**: Monthly payment tracking
- **documents**: File storage and metadata

## File Structure

```
sidharat-hostels/
├── app.py              # Main Flask application
├── requirements.txt    # Dependencies
├── hostel.db          # SQLite database
├── uploads/           # Document storage
└── templates/         # HTML templates
    ├── base.html
    ├── index.html
    ├── add_student.html
    ├── rooms.html
    ├── rents.html
    ├── documents.html
    ├── student_documents.html
    └── search_results.html
```

## Configuration

### Room Layout
- Ground Floor: Rooms 1-5 (default)
- First Floor: Rooms 101-120
- Second Floor: Rooms 201-220

### Default Settings
- Room capacity: 2 beds
- Monthly rent: ₹5,000
- File upload limit: 16MB
- Supported formats: PDF, JPG, PNG, DOC, DOCX

## Security Features

- Input validation and sanitization
- Secure filename handling
- File type restrictions
- SQL injection prevention
- XSS protection via Flask

## Browser Support

- Chrome, Firefox, Safari, Edge
- Mobile responsive design
- Bootstrap 5 UI framework

## Support

For issues or questions, check the application logs or database for debugging information.