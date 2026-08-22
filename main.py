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
    Set up the database by creating necessary tables
    """
    create_trip_info_table()
    create_activity_table()
    create_hotel_table()
    create_extra_costs_table()
    create_flight_table()

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
                    travel_mode TEXT,
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

def create_hotel_table():
    """
    Create a table for storing hotel information related to trips in the database.
    """
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE Hotels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_id INTEGER NOT NULL,
                hotel_name TEXT NOT NULL,
                check_in_date DATE NOT NULL,
                check_out_date DATE NOT NULL,
                location TEXT,
                cost_per_day REAL,
                num_days INTEGER,
                description TEXT,
                FOREIGN KEY (trip_id) REFERENCES TripInfo(id)
            )
        ''')
        connection.commit()
        connection.close()
    except Exception as e:
        print(f"Database initialization error: {e}")

def create_flight_table():
    """
    Create a table for storing flight information related to trips in the database.
    """
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE Flights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_id INTEGER NOT NULL,
                airline TEXT NOT NULL,
                flight_number TEXT NOT NULL,
                departure_date DATE NOT NULL,
                departure_time TIME NOT NULL,
                arrival_date DATE NOT NULL,
                arrival_time TIME NOT NULL,
                cost REAL,
                description TEXT,
                FOREIGN KEY (trip_id) REFERENCES TripInfo(id)
            )
        ''')
        connection.commit()
        connection.close()
    except Exception as e:
        print(f"Database initialization error: {e}")

def create_extra_costs_table():
    """
    Create a table for storing extra costs related to trips in the database.
    """
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE ExtraCosts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_id INTEGER NOT NULL,
                cost_name TEXT NOT NULL,
                cost_amount REAL NOT NULL,
                cost_date DATE NOT NULL,
                description TEXT,
                FOREIGN KEY (trip_id) REFERENCES TripInfo(id)
            )
        ''')
        connection.commit()
        connection.close()
    except Exception as e:
        print(f"Database initialization error: {e}")

# --- Add into Database ---
def add_trip(trip_data):
    """
    Save a new trip to the database and returns true if successful, false otherwise.
    :param trip_data: Dictionary containing trip information
    :return: Boolean indicating success or failure
    """
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO TripInfo 
            (trip_name, destination, country, start_date, end_date, budget, num_travelers, description, travel_mode, companions)
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
            trip_data.get('travel_mode'),
            trip_data.get('companions')
        ))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"Error creating trip: {e}")
        return False
    
def add_activity(activity_data):
    """
    Save a new activity to the database and returns true if successful, false otherwise.
    :param activity_data: Dictionary containing activity information
    :return: Boolean indicating success or failure
    """
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO Activities 
            (trip_id, activity_name, activity_type, activity_date, activity_time, location, description, cost)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            activity_data.get('trip_id'),
            activity_data.get('activity_name'),
            activity_data.get('activity_type'),
            activity_data.get('activity_date'),
            activity_data.get('activity_time'),
            activity_data.get('location'),
            activity_data.get('description'),
            activity_data.get('cost') or 0
        ))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"Error creating activity: {e}")
        return False
    
def add_hotel(hotel_data):
    """
    Save a new hotel to the database and returns true if successful, false otherwise.
    :param hotel_data: Dictionary containing hotel information
    :return: Boolean indicating success or failure
    """
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO Hotels 
            (trip_id, hotel_name, check_in_date, check_out_date, location, cost_per_day, num_days, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            hotel_data.get('trip_id'),
            hotel_data.get('hotel_name'),
            hotel_data.get('check_in_date'),
            hotel_data.get('check_out_date'),
            hotel_data.get('location'),
            hotel_data.get('cost_per_day') or 0,
            hotel_data.get('num_days') or 1,
            hotel_data.get('description')
        ))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"Error creating hotel: {e}")
        return False
    
def add_flight(flight_data):
    """
    Save a new flight to the database and returns true if successful, false otherwise.
    :param flight_data: Dictionary containing flight information
    :return: Boolean indicating success or failure
    """
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO Flights 
            (trip_id, airline, flight_number, departure_date, departure_time, arrival_date, arrival_time, cost, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            flight_data.get('trip_id'),
            flight_data.get('airline'),
            flight_data.get('flight_number'),
            flight_data.get('departure_date'),
            flight_data.get('departure_time'),
            flight_data.get('arrival_date'),
            flight_data.get('arrival_time'),
            flight_data.get('cost') or 0,
            flight_data.get('description')
        ))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"Error creating flight: {e}")
        return False
    
def add_extra_cost(extra_cost_data):
    """
    Save a new extra cost to the database and returns true if successful, false otherwise.
    :param extra_cost_data: Dictionary containing extra cost information
    :return: Boolean indicating success or failure
    """
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO ExtraCosts 
            (trip_id, cost_name, cost_amount, cost_date, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            extra_cost_data.get('trip_id'),
            extra_cost_data.get('cost_name'),
            extra_cost_data.get('cost_amount') or 0,
            extra_cost_data.get('cost_date'),
            extra_cost_data.get('description')
        ))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"Error creating extra cost: {e}")
        return False

# --- Retrieve Database Information ---
def get_trips():
    """
    Retrieve all trips from the database
    :return: List of trips
    """
    try:
        connection = sqlite3.connect(database_name)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        trips = cursor.execute('''
            SELECT
                * 
            FROM 
                TripInfo 
            ORDER BY 
                start_date DESC''').fetchall()
        connection.close()
        return trips
    except Exception as e:
        print(f"Error retrieving trips: {e}")
        return []

def get_activities(trip_id):
    """
    Retrieve all activities for a specific trip from the database
    :param trip_id: ID of the trip
    :return: List of activities
    """
    try:
        connection = sqlite3.connect(database_name)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        activities = cursor.execute('''
            SELECT 
                * 
            FROM 
                Activities 
            WHERE 
                trip_id = ? 
            ORDER BY 
                activity_date ASC''', (trip_id,)).fetchall()
        connection.close()
        return activities
    except Exception as e:
        print(f"Error retrieving activities: {e}")
        return []
    
def get_hotels(trip_id):
    """
    Retrieve all hotels for a specific trip from the database
    :param trip_id: ID of the trip
    :return: List of hotels
    """
    try:
        connection = sqlite3.connect(database_name)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        hotels = cursor.execute('''
            SELECT 
                * 
            FROM 
                Hotels 
            WHERE 
                trip_id = ? 
            ORDER BY 
                check_in_date ASC''', (trip_id,)).fetchall()
        connection.close()
        return hotels
    except Exception as e:
        print(f"Error retrieving hotels: {e}")
        return []

def get_flights(trip_id):
    """
    Retrieve all flights for a specific trip from the database
    :param trip_id: ID of the trip
    :return: List of flights
    """
    try:
        connection = sqlite3.connect(database_name)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        flights = cursor.execute('''
            SELECT 
                * 
            FROM 
                Flights 
            WHERE 
                trip_id = ? 
            ORDER BY 
                departure_date ASC''', (trip_id,)).fetchall()
        connection.close()
        return flights
    except Exception as e:
        print(f"Error retrieving flights: {e}")
        return []
    
def get_extra_costs(trip_id):
    """
    Retrieve all extra costs for a specific trip from the database
    :param trip_id: ID of the trip
    :return: List of extra costs
    """
    try:
        connection = sqlite3.connect(database_name)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        extra_costs = cursor.execute('''
            SELECT 
                * 
            FROM 
                ExtraCosts 
            WHERE 
                trip_id = ? 
            ORDER BY 
                cost_date ASC''', (trip_id,)).fetchall()
        connection.close()
        return extra_costs
    except Exception as e:
        print(f"Error retrieving extra costs: {e}")
        return []

# --- Delete Database Information ---
def delete_flight_record(trip_id, flight_id):
    """
    Delete a flight from the database for a specific trip
    :param trip_id: ID of the trip
    :param flight_id: ID of the flight to delete
    :return: Boolean indicating success or failure
    """
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        cursor.execute('''
            DELETE FROM 
                Flights 
            WHERE 
                id = ? 
            AND 
                trip_id = ?''', (flight_id, trip_id))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"Error deleting flight: {e}")
        return False

def delete_hotel_record(trip_id, hotel_id):
    """
    Delete a hotel from the database for a specific trip
    :param trip_id: ID of the trip
    :param hotel_id: ID of the hotel to delete
    :return: Boolean indicating success or failure
    """
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        cursor.execute('''
            DELETE FROM 
                Hotels 
            WHERE 
                id = ? 
            AND 
                trip_id = ?''', (hotel_id, trip_id))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"Error deleting hotel: {e}")
        return False

# --- Webpages ---
@app.route("/", methods=['GET', 'POST'])
def home():
    """
    Add a new trip.
    """
    if request.method == 'POST':
        # Extract form data
        trip_data = {
            'trip_name': request.form.get('trip_name'),
            'destination': request.form.get('destination'),
            'country': request.form.get('country'),
            'start_date': request.form.get('start_date'),
            'end_date': request.form.get('end_date'),
            'budget': request.form.get('budget'),
            'num_travelers': request.form.get('num_travelers'),
            'description': request.form.get('description'),
            'travel_mode': request.form.get('travel_mode'),
            'companions': request.form.get('companions')
        }

        if not all([trip_data['trip_name'], trip_data['destination'], 
                    trip_data['start_date'], trip_data['end_date']]):
            flash('Please fill in all required fields!', 'error')
        else:
            if add_trip(trip_data):
                flash(f"Trip '{trip_data['trip_name']}' created successfully!", 'success')
                return redirect(url_for('view_trips'))
            else:
                flash('Error creating trip. Please try again.', 'error')

    return render_template("home.html")

@app.route("/trips")
def view_trips():
    """
    View all trips.
    """
    trips = get_trips()
    return render_template("trips.html", trips=trips)


@app.route('/plan/<int:trip_id>')
def plan_trip(trip_id):
    """
    Plan a specific trip by id.
    """
    try:
        connection = sqlite3.connect(database_name)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM TripInfo WHERE id = ?', (trip_id,))
        trip = cursor.fetchone()
        connection.close()

        if trip is None:
            flash('Trip not found.', 'error')
            return redirect(url_for('view_trips'))

        # Fetch related data
        activities = get_activities(trip_id)
        hotels = get_hotels(trip_id)
        flights = get_flights(trip_id)

        return render_template('plan.html', trip=trip, activities=activities, hotels=hotels, flights=flights)
    except Exception as e:
        print(f"Error loading trip for planning: {e}")
        flash('Error loading trip.', 'error')
        return redirect(url_for('view_trips'))
    
@app.route('/add_activity/<int:trip_id>', methods=['POST'])
def add_activity_route(trip_id):
    """
    Add a new activity to a specific trip.
    """
    pass

@app.route('/add_hotel_route/<int:trip_id>', methods=['GET', 'POST'])
def add_hotel_route(trip_id):
    """
    Add a new hotel to a specific trip.
    """
    try:
        connection = sqlite3.connect(database_name)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM TripInfo WHERE id = ?', (trip_id,))
        trip = cursor.fetchone()
        connection.close()

        if trip is None:
            flash('Trip not found.', 'error')
            return redirect(url_for('view_trips'))
        
        hotels = get_hotels(trip_id)

    except Exception as e:
        print(f"Error loading trip for planning: {e}")
        flash('Error loading add hotel page.', 'error')
        return redirect(url_for('view_trips'))

    if request.method == 'POST':
        hotel_data = {
            'trip_id': trip_id,
            'hotel_name': request.form.get('hotel_name'),
            'check_in_date': request.form.get('check_in_date'),
            'check_out_date': request.form.get('check_out_date'),
            'location': request.form.get('location'),
            'cost_per_day': request.form.get('cost_per_day'),
            'num_days': request.form.get('num_days'),
            'description': request.form.get('description')
        }

        if not all([hotel_data['hotel_name'], hotel_data['check_in_date'], hotel_data['check_out_date']]):
            flash('Please fill in all required fields for the hotel!', 'error')
        else:
            if add_hotel(hotel_data):
                flash(f"Hotel '{hotel_data['hotel_name']}' added successfully!", 'success')
            else:
                flash('Error adding hotel. Please try again.', 'error')

        return redirect(url_for('plan_trip', trip_id=trip_id))
    return render_template('add_hotel_route.html', trip_id=trip_id, trip=trip, hotels=hotels)
    

@app.route('/add_extra_cost/<int:trip_id>', methods=['POST'])
def add_extra_cost_route(trip_id):
    """
    Add a new extra cost to a specific trip.
    """
    pass

@app.route('/add_flight_route/<int:trip_id>', methods=['GET', 'POST'])
def add_flight_route(trip_id):
    """
    Add a new flight to a specific trip.
    """
    try:
        connection = sqlite3.connect(database_name)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM TripInfo WHERE id = ?', (trip_id,))
        trip = cursor.fetchone()
        connection.close()

        if trip is None:
            flash('Trip not found.', 'error')
            return redirect(url_for('view_trips'))
        
        flights = get_flights(trip_id)

    except Exception as e:
        print(f"Error loading trip for planning: {e}")
        flash('Error loading add flight page.', 'error')
        return redirect(url_for('view_trips'))

    if request.method == 'POST':
        flight_data = {
            'trip_id': trip_id,
            'airline': request.form.get('airline'),
            'flight_number': request.form.get('flight_number'),
            'departure_date': request.form.get('departure_date'),
            'departure_time': request.form.get('departure_time'),
            'arrival_date': request.form.get('arrival_date'),
            'arrival_time': request.form.get('arrival_time'),
            'cost': request.form.get('cost'),
            'description': request.form.get('description')
        }

        if not all([flight_data['airline'], flight_data['flight_number'], flight_data['departure_date'], flight_data['arrival_date']]):
            flash('Please fill in all required fields for the flight!', 'error')
        else:
            if add_flight(flight_data):
                flash(f"Flight '{flight_data['flight_number']}' added successfully!", 'success')
            else:
                flash('Error adding flight. Please try again.', 'error')

        return redirect(url_for('plan_trip', trip_id=trip_id))
    
    return render_template('add_flight_route.html', trip_id=trip_id, trip=trip, flights=flights)

# --- Delete Routes ---
@app.route('/delete_flight/<int:flight_id>/<int:trip_id>')
def delete_flight(flight_id, trip_id):
    """
    Delete a flight from a specific trip.
    :param flight_id: ID of the flight to delete
    :param trip_id: ID of the trip the flight belongs to
    """
    if delete_flight_record(trip_id, flight_id):
        flash('Flight deleted successfully.', 'success')
    else:
        flash('Error deleting flight. Please try again.', 'error')

    return redirect(url_for('plan_trip', trip_id=trip_id))

@app.route('/delete_hotel/<int:hotel_id>/<int:trip_id>')
def delete_hotel(hotel_id, trip_id):
    """
    Delete a hotel from a specific trip.
    :param hotel_id: ID of the hotel to delete
    :param trip_id: ID of the trip the hotel belongs to
    """
    if delete_hotel_record(trip_id, hotel_id):
        flash('Hotel deleted successfully.', 'success')
    else:
        flash('Error deleting hotel. Please try again.', 'error')

    return redirect(url_for('plan_trip', trip_id=trip_id))


if __name__ == "__main__":
    global database_name
    database_name = 'trips.db' # Set the database name

    first_run = True

    if (pathlib.Path.cwd() / database_name).exists():
        first_run = False
    
    if first_run:
        set_up_database() # Set up the database if it's the first run

    app.run(debug=True) # Run the flask app









