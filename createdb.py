from property import app, db

# Inside the Python shell or script where you need to perform database operations:
with app.app_context():
    db.create_all()
