from app import app, db
from app import User

# Run the script within the application context
with app.app_context():
    # Create the database and the database table(s)
    db.create_all()

    # Commit the changes
    db.session.commit()