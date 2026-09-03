import sqlite3
from datetime import datetime, timedelta, date

from weather_information import get_weather

database_name = 'trips.db'

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
    create_weather_info_table()

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
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                weather_updated_at DATE NOT NULL
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
                name TEXT NOT NULL,
                cost REAL NOT NULL,
                date DATE NOT NULL,
                description TEXT,
                FOREIGN KEY (trip_id) REFERENCES TripInfo(id)
            )
        ''')
        connection.commit()
        connection.close()
    except Exception as e:
        print(f"Database initialization error: {e}")

def create_weather_info_table():
    """
    Create a table to store daily weather information for the trip.
    """
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE WeatherInfo (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trip_id INTEGER NOT NULL,
                weather_date DATE NOT NULL,
                temperature_max REAL,
                temperature_min REAL,
                precipitation_probability REAL,
                precipitation_sum REAL,
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
    Also calls weather api to get weather information and save those data into the database.
    This function works on this additional task because it has access to the id of the latest trip, which by default is set to autoincrement
    :param trip_data: Dictionary containing trip information
    :return: Boolean indicating success or failure
    """
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO TripInfo 
            (trip_name, destination, country, start_date, end_date, budget, num_travelers, description, travel_mode, companions, weather_updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            trip_data.get('companions'),
            trip_data.get('start_date')
        ))
        trip_id = cursor.lastrowid
        connection.commit()
        connection.close()

        store_weather_for_trip(
            trip_id,
            trip_data.get('destination'),
            trip_data.get('country'),
            trip_data.get('start_date'),
            trip_data.get('end_date')
        )

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
            (trip_id, name, cost, date, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            extra_cost_data.get('trip_id'),
            extra_cost_data.get('name'),
            extra_cost_data.get('cost') or 0,
            extra_cost_data.get('date'),
            extra_cost_data.get('description')
        ))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"Error creating extra cost: {e}")
        return False

def add_weather_info(weather_data):
    """
    Saves new weather information for a particular day into the database and returns true if successful, false otherwise.
    :param weather_data: Dictionary containing weather information
    :return: Boolean indicating success or failure
    """
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO WeatherInfo
            (trip_id, weather_date, temperature_max, temperature_min, precipitation_probability, precipitation_sum)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            weather_data.get('trip_id'),
            weather_data.get('weather_date'),
            weather_data.get('temperature_max'),
            weather_data.get('temperature_min'),
            weather_data.get('precipitation_probability'),
            weather_data.get('precipitation_sum')
        ))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"Error creating weather information: {e}")
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
                start_date ASC''').fetchall()
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
                activity_date ASC,
                activity_time ASC''', (trip_id,)).fetchall()
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
                date ASC''', (trip_id,)).fetchall()
        connection.close()
        return extra_costs
    except Exception as e:
        print(f"Error retrieving extra costs: {e}")
        return []

def get_weather_info(trip_id):
    """
    Retrieve all weather data for a specific trip from the database
    :param trip_id: ID of the trip
    :return: List of weather information
    """
    try:
        connection = sqlite3.connect(database_name)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        weather_info = cursor.execute('''
            SELECT 
                * 
            FROM 
                WeatherInfo 
            WHERE 
                trip_id = ? 
            ORDER BY 
                weather_date ASC''', (trip_id,)).fetchall()
        connection.close()
        return weather_info
    except Exception as e:
        print(f"Error retrieving weather information: {e}")
        return []
    
# --- Get Single Item From Database ---
def get_single_trip(trip_id):
    """
    Retrieve a single trip from the database
    :param trip_id: ID of the trip to retrieve
    :return: The trip as a dictionary or None if not found
    """
    if trip_id is None:
        return None
    
    connection = sqlite3.connect(database_name)
    connection.row_factory = sqlite3.Row

    trip = connection.execute('''
        SELECT 
            * 
        FROM 
            TripInfo 
        WHERE 
            id = ?''', (trip_id,)
    ).fetchone()
    connection.close()
    return trip

def get_item_to_edit(item_type, item_id):
    """
    retrieve a single item (activity, hotel, flight, or extra cost) from the database of a trip for editing
    :param item_type: Type of the item (activity, hotel, flight, extra_cost)
    :param item_id: ID of the item to retrieve
    :return: The item as a dictionary or None if not found
    """
    if item_id is None:
        return None
    
    table_names_map = {
        "hotels": "Hotels",
        "flights": "Flights",
        "activities": "Activities",
        "extra_costs": "ExtraCosts"
    }

    table_name = table_names_map.get(item_type)

    if table_name is None:
        print(f"Invalid item type: {item_type}")
        return None
    
    connection = sqlite3.connect(database_name)
    connection.row_factory = sqlite3.Row

    item = connection.execute(f'''
        SELECT 
            * 
        FROM 
            {table_name} 
        WHERE 
            id = ?''', (item_id,)
    ).fetchone()
    connection.close()

    return item

# --- Update Database Information Of Single Rows ---
def update_trip(trip_id, trip_data):
    """
    Update a trip in the database for a specific trip ID
    :param trip_id: ID of the trip to update
    :param trip_data: Dictionary containing updated trip information
    :return: Boolean indicating success or failure
    """
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        cursor.execute('''
            UPDATE 
                TripInfo 
            SET 
                trip_name = ?, 
                destination = ?, 
                country = ?, 
                start_date = ?, 
                end_date = ?, 
                budget = ?, 
                num_travelers = ?, 
                description = ?, 
                travel_mode = ?, 
                companions = ?,
                weather_updated_at = ?
            WHERE 
                id = ?''', (
                    trip_data.get('trip_name'),
                    trip_data.get('destination'),
                    trip_data.get('country'),
                    trip_data.get('start_date'),
                    trip_data.get('end_date'),
                    trip_data.get('budget') or 0,
                    trip_data.get('num_travelers') or 1,
                    trip_data.get('description'),
                    trip_data.get('travel_mode'),
                    trip_data.get('companions'),
                    trip_data.get('start_date'),
                    trip_id
                ))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"Error updating trip: {e}")
        return False

def update_flight(flight_id, flight_data):
    """
    Update a flight in the database for a specific flight ID
    :param flight_id: ID of the flight to update
    :param flight_data: Dictionary containing updated flight information
    :return: Boolean indicating success or failure
    """
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        cursor.execute('''
            UPDATE 
                Flights 
            SET 
                airline = ?, 
                flight_number = ?, 
                departure_date = ?, 
                departure_time = ?, 
                arrival_date = ?, 
                arrival_time = ?, 
                cost = ?, 
                description = ? 
            WHERE 
                id = ?''', (
                    flight_data.get('airline'),
                    flight_data.get('flight_number'),
                    flight_data.get('departure_date'),
                    flight_data.get('departure_time'),
                    flight_data.get('arrival_date'),
                    flight_data.get('arrival_time'),
                    flight_data.get('cost') or 0,
                    flight_data.get('description'),
                    flight_id
                ))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"Error updating flight: {e}")
        return False

def update_hotel(hotel_id, hotel_data):
    """
    Update a hotel in the database for a specific hotel ID
    :param hotel_id: ID of the hotel to update
    :param hotel_data: Dictionary containing updated hotel information
    :return: Boolean indicating success or failure
    """
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        cursor.execute('''
            UPDATE 
                Hotels 
            SET 
                hotel_name = ?, 
                check_in_date = ?, 
                check_out_date = ?, 
                location = ?, 
                cost_per_day = ?, 
                num_days = ?, 
                description = ? 
            WHERE 
                id = ?''', (
                    hotel_data.get('hotel_name'),
                    hotel_data.get('check_in_date'),
                    hotel_data.get('check_out_date'),
                    hotel_data.get('location'),
                    hotel_data.get('cost_per_day') or 0,
                    hotel_data.get('num_days') or 1,
                    hotel_data.get('description'),
                    hotel_id
                ))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"Error updating hotel: {e}")
        return False

def update_activity(activity_id, activity_data):
    """
    Update an activity in the database for a specific activity ID
    :param activity_id: ID of the activity to update
    :param activity_data: Dictionary containing updated activity information
    :return: Boolean indicating success or failure
    """
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        cursor.execute('''
            UPDATE 
                Activities 
            SET 
                activity_name = ?, 
                activity_type = ?, 
                activity_date = ?, 
                activity_time = ?, 
                location = ?, 
                description = ?, 
                cost = ? 
            WHERE 
                id = ?''', (
                    activity_data.get('activity_name'),
                    activity_data.get('activity_type'),
                    activity_data.get('activity_date'),
                    activity_data.get('activity_time'),
                    activity_data.get('location'),
                    activity_data.get('description'),
                    activity_data.get('cost') or 0,
                    activity_id
                ))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"Error updating activity: {e}")
        return False

def update_extra_cost(extra_cost_id, extra_cost_data):
    """
    Updates an extra cost in the database for a specific extra cost ID
    :param extra_cost_id: ID of the extra cost to update
    :param extra_cost_data: Dictionary containing updated extra cost information
    :return: Boolean indicating success or failure
    """
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        cursor.execute('''
            UPDATE
                ExtraCosts
            SET
                name = ?,
                cost = ?,
                date = ?,
                description = ?
            WHERE
                id = ?''', (
                    extra_cost_data.get('name'),
                    extra_cost_data.get('cost') or 0,
                    extra_cost_data.get('date'),
                    extra_cost_data.get('description'),
                    extra_cost_id
                ))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"Error updating extra cost: {e}")
        return False

def update_weather_info(weather_info_id, new_weather_data):
    """
    Updates a weather info of a specific day in the database with new information
    :param weather_info_id: ID of the weather row to update
    :param new_weather_data: Dictionary containing updated weather information
    :return: Boolean indicating success or failure
    """
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        cursor.execute('''
            UPDATE
                WeatherInfo
            SET
                temperature_max = ?,
                temperature_min = ?,
                precipitation_probability = ?,
                precipitation_sum = ?
            WHERE
                id = ?''', (
                    new_weather_data.get('temperature_max'),
                    new_weather_data.get('temperature_min') or 0,
                    new_weather_data.get('precipitation_probability'),
                    new_weather_data.get('precipitation_sum'),
                    weather_info_id
                ))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"Error updating weather information: {e}")
        return False

def update_trip_weather_date(trip_id, new_weather_date):
    """
    Changes the weather_updated_at column in TripInfo to new_weather_date
    :param trip_id: ID of the trip
    :param new_weather_date: New date as a string in YYYY-MM-DD format
    :return: Boolean indicating success or failure
    """
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        cursor.execute('''
            UPDATE 
                TripInfo 
            SET 
                weather_updated_at = ?
            WHERE 
                id = ?''', (
                    new_weather_date,
                    trip_id
                ))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"Error updating trip: {e}")
        return False

# --- Delete Database Information Of Single Rows ---
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

def delete_activity_record(trip_id, activity_id):
    """
    Delete an activity from the database for a specific trip
    :param trip_id: ID of the trip
    :param activity_id: ID of the activity to delete
    :return: Boolean indicating success or failure
    """
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        cursor.execute('''
            DELETE FROM 
                Activities 
            WHERE 
                id = ? 
            AND 
                trip_id = ?''', (activity_id, trip_id))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"Error deleting activity: {e}")
        return False

def delete_extra_cost_record(trip_id, extra_cost_id):
    """
    Delete an extra_cost from the database for a specific trip
    :param trip_id: ID of the trip
    :param extra_cost_id: ID of the extra cost to delete
    :return: Boolean indicating success or failure
    """
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        cursor.execute('''
            DELETE FROM 
                ExtraCosts 
            WHERE 
                id = ? 
            AND 
                trip_id = ?''', (extra_cost_id, trip_id))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"Error deleting extra cost: {e}")
        return False

# --- Delete All Weather Info for a Trip ---
def delete_trip_weather_info(trip_id, cutoff_date):
    """
    Delete all weather information for all days associated with a specific trip that is after cutoff_date
    :param trip_id: ID of the trip
    :param cutoff_date: Represents a string date in YYYY-MM-DD
    :return: Boolean indicating success or failure
    """
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()
        cursor.execute('''
            DELETE FROM
                WeatherInfo
            WHERE
                trip_id = ?
            AND
                weather_date >= ?
        ''', (trip_id, cutoff_date))
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"Error deleting weather information: {e}")
        return False

# --- Delete Entire Trip and Associated Records ---
def delete_trip_and_associated_records(trip_id):
    """
    Delete a trip and all associated records (flights, hotels, activities, extra costs).
    :param trip_id: ID of the trip to delete
    :return: Boolean indicating success or failure
    """
    try:
        connection = sqlite3.connect(database_name)
        cursor = connection.cursor()

        # Delete associated records
        cursor.execute('DELETE FROM Flights WHERE trip_id = ?', (trip_id,))
        cursor.execute('DELETE FROM Hotels WHERE trip_id = ?', (trip_id,))
        cursor.execute('DELETE FROM Activities WHERE trip_id = ?', (trip_id,))
        cursor.execute('DELETE FROM ExtraCosts WHERE trip_id = ?', (trip_id,))
        cursor.execute('DELETE FROM WeatherInfo WHERE trip_id = ?', (trip_id,))

        # Delete the trip itself
        cursor.execute('DELETE FROM TripInfo WHERE id = ?', (trip_id,))

        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(f"Error deleting trip and associated records: {e}")
        return False
    
def get_available_forecast_dates(start_date, end_date):
    """
    Finds days between start_date and end_date with available weather information
    The Open-Meteo 14-day forecast window is capped to 14 days from today.
    :param start_date: Date as a string in YYYY-MM-DD format
    :param end_date: Date as a string in YYYY-MM-DD format
    :return: Date, Date indicating the start and end dates with available forecast, or None, indicating there are no days to with available forecast
    """
    max_forecast_days = 14

    trip_start = datetime.strptime(start_date, "%Y-%m-%d").date()
    trip_end = datetime.strptime(end_date, "%Y-%m-%d").date()

    today = datetime.today().date()
    latest_forecast_date = today + timedelta(days=max_forecast_days)

    # Entire trip is in the past
    if trip_end < today:
        return None

    # Entire trip is too far in the future
    if trip_start > latest_forecast_date:
        return None

    # Don't request dates before today
    forecast_start = max(trip_start, today)

    # Don't request dates beyond the forecast range
    forecast_end = min(trip_end, latest_forecast_date)

    return forecast_start, forecast_end

def store_weather_for_trip(trip_id, city, country, start_date, end_date):
    """
    Fetch weather data for a trip and save each day into the WeatherInfo table.
    Days outside the 14-day forecast window are still saved with NULL values.
    :param city: name of city as a string
    :param country: name of country as a string
    :param start_date: date string in YYYY-MM-DD format
    :param end_date: date string in YYYY-MM-DD format
    :return: Boolean indicating success or failure
    """
    if trip_id is None or not city or not start_date or not end_date:
        return False

    # Remove any pre-existing information in the future that could still be updated
    delete_trip_weather_info(trip_id, date.today().isoformat())

    forecast_window = get_available_forecast_dates(start_date, end_date)
    weather_lookup = {}

    if forecast_window is not None:
        forecast_start, forecast_end = forecast_window
        try:
            weather_data = get_weather(city, country or '', forecast_start.isoformat(), forecast_end.isoformat())
        except Exception as e:
            print(f"Error fetching weather forecast: {e}")
            weather_data = None

        if weather_data:
            dates = weather_data.get('time', [])
            max_temps = weather_data.get('temperature_2m_max', [])
            min_temps = weather_data.get('temperature_2m_min', [])
            precipitation_probabilities = weather_data.get('precipitation_probability_max', [])
            precipitation_sums = weather_data.get('precipitation_sum', [])

            for i, weather_date in enumerate(dates):
                weather_lookup[weather_date] = {
                    'temperature_max': max_temps[i] if i < len(max_temps) else None,
                    'temperature_min': min_temps[i] if i < len(min_temps) else None,
                    'precipitation_probability': precipitation_probabilities[i] if i < len(precipitation_probabilities) else None,
                    'precipitation_sum': precipitation_sums[i] if i < len(precipitation_sums) else None,
                }

    trip_start = datetime.strptime(start_date, '%Y-%m-%d').date()
    trip_end = datetime.strptime(end_date, '%Y-%m-%d').date()
    current_date = max(trip_start, date.today())

    while current_date <= trip_end:
        weather_key = current_date.isoformat()
        row_data = weather_lookup.get(weather_key, {})

        weather_info = {
            'trip_id': trip_id,
            'weather_date': weather_key,
            'temperature_max': row_data.get('temperature_max'),
            'temperature_min': row_data.get('temperature_min'),
            'precipitation_probability': row_data.get('precipitation_probability'),
            'precipitation_sum': row_data.get('precipitation_sum'),
        }
        add_weather_info(weather_info)
        current_date += timedelta(days=1)

    return True