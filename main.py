# --- Additional libraries ---
from flask import Flask, render_template, request, redirect, flash, url_for
import pathlib
import sqlite3
from datetime import datetime
import pathlib

app = Flask(__name__) # Create the flask app
app.secret_key = 'travel_planner_secret_key' # For flash messages

# --- Database Setup ---
def set_up_database():
    """
    Set up the database by creating necessary tables if they don't exist.
    """
    create_trip_info_table()
    create_activity_table()

def create_trip_info_table():
    """
    Create a table for storing trip information in the database.
    """
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE TripInfo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_name TEXT NOT NULL,
                destination TEXT NOT NULL,
                country TEXT,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                budget REAL,
                num_travelers INTEGER DEFAULT 1,
                description TEXT,
                travel_style TEXT,
                companions TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        connection.commit()
        connection.close()
    except Exception as e:
        print(f"Database initialization error: {e}")

def create_activity_table():
    """
    Create a table for storing activities related to trips in the database.
    """
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE Activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_id INTEGER NOT NULL,
                activity_name TEXT NOT NULL,
                activity_type TEXT,
                activity_date DATE NOT NULL,
                activity_time TIME,
                location TEXT,
                description TEXT,
                cost REAL,
                FOREIGN KEY (trip_id) REFERENCES TripInfo(id)
            )
        ''')
        connection.commit()
        connection.close()
    except Exception as e:
        print(f"Database initialization error: {e}")

def get_trips():
    """
    Retrieve all trips from the database
    """
    try:
        connection = sqlite3.connect(database_name)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM trips ORDER BY start_date DESC')
        trips = cursor.fetchall()
        connection.close()
        return trips
    except Exception as e:
        print(f"Error retrieving trips: {e}")
        return []

def create_trip(trip_data):
    """
    Save a new trip to the database
    """
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO trips 
            (trip_name, destination, country, start_date, end_date, budget, travelers, description, travel_style, companions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            trip_data.get('trip_name'),
            trip_data.get('destination'),
            trip_data.get('country'),
            trip_data.get('start_date'),
            trip_data.get('end_date'),
            trip_data.get('budget') or 0,
            trip_data.get('num_travelers') or 1,
            trip_data.get('description'),
            trip_data.get('travel_style'),
            trip_data.get('companions')
        ))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"Error creating trip: {e}")
        return False

# --- Webpages ---
@app.route("/", methods=['GET', 'POST'])
def home():
    trips = []
    
    if request.method == 'POST':
        # Extract form data
        trip_data = {
            'trip_name': request.form.get('trip_name'),
            'destination': request.form.get('destination'),
            'country': request.form.get('country'),
            'start_date': request.form.get('start_date'),
            'end_date': request.form.get('end_date'),
            'budget': request.form.get('budget'),
            'travelers': request.form.get('travelers'),
            'description': request.form.get('description'),
            'travel_style': request.form.get('travel_style'),
            'companions': request.form.get('companions')
        }
    
    # Get all trips to display
    trips = get_trips()
    
    return render_template("home.html", trips=trips)

if __name__ == "__main__":
    global database_name
    database_name = 'trips.db' # Set the database name

    first_run = True

    if (pathlib.Path.cwd() / database_name).exists():
        first_run = False
    
    if first_run:
        set_up_database() # Set up the database if it's the first run

    app.run(debug=True) # Run the flask app









