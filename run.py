from app import app, init_db

if __name__ == '__main__':
    init_db()
    print("🏨 Sidharat Hostels Management System")
    print("📊 Dashboard: http://localhost:5000")
    print("🚀 Starting server...")
    app.run(debug=True, host='0.0.0.0', port=5000)