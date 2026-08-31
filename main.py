# --- Additional libraries ---
from flask import Flask, render_template, request, redirect, flash, url_for
import pathlib
import sqlite3
from datetime import datetime, timedelta, date
import pathlib
from google import genai

from weather_information import get_weather

app = Flask(__name__) # Create the flask app
app.secret_key = 'travel_planner_secret_key' # For flash messages

# Gemini API variables
chat_history = []
client = genai.Client(api_key="AQ.Ab8RN6Kfg482nJWm7h6ICp-xDfiFVww8tFFUmMT7FDPVgU_7gA")

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
    Retrieve a single trip from the database for editing
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

# --- Webpages ---
@app.route("/", methods=['GET', 'POST'])
@app.route("/<int:trip_id>", methods=['GET', 'POST'])
def home(trip_id=None):
    """
    Add a new trip.
    """

    trip_to_edit = None

    if trip_id is not None:
        trip_to_edit = get_single_trip(trip_id)
        if trip_to_edit is None:
            flash('Trip not found for editing.', 'error')
            return redirect(url_for('home'))

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

        if check_valid_trip_date(trip_data['start_date'], trip_data['end_date']) is True:
            if trip_id is not None:
                if update_trip(trip_id, trip_data):
                    # Add new weather information
                    try:
                        store_weather_for_trip(trip_id, trip_data.get('destination'), trip_data.get('country'), trip_data.get('start_date'), trip_data.get('end_date'))
                    except Exception as e:
                        print(f"Error updating weather for trip: {e}")

                    flash(f"Trip '{trip_data['trip_name']}' updated successfully!", 'success')
                else:
                    flash('Error updating trip. Please try again.', 'error')
                return redirect(url_for('view_trips'))

            if add_trip(trip_data):
                flash(f"Trip '{trip_data['trip_name']}' created successfully!", 'success')
                return redirect(url_for('view_trips'))
            else:
                flash('Error creating trip. Please try again.', 'error')
        else:
            flash('Error! End date cannot be before start date, or start date cannot be before today.', 'error')
        return redirect(url_for('home'))

    return render_template("home.html", trip_to_edit=trip_to_edit)

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
        extra_costs = get_extra_costs(trip_id)

        # Calculate total costs
        all_costs = {
            'activities': calculate_total_event_cost(activities),
            'hotels': calculate_hotel_total_cost(hotels),
            'flights': calculate_total_event_cost(flights),
            'extra_costs': calculate_total_event_cost(extra_costs),
            'total_cost': calculate_overall_cost(trip_id)
        }

    except Exception as e:
        print(f"Error loading trip for planning: {e}")
        flash('Error loading trip.', 'error')
        return redirect(url_for('view_trips'))
    
    return render_template('plan.html', trip=trip, trip_id= trip_id, activities=activities, hotels=hotels, flights=flights, extra_costs=extra_costs, all_costs=all_costs)
    
@app.route('/add_activity_route/<int:trip_id>', methods=['GET', 'POST'])
@app.route('/add_activity_route/<int:trip_id>/<int:activity_id>', methods=['GET', 'POST'])
def add_activity_route(trip_id, activity_id=None):
    """
    Add a new activity to a specific trip.
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

        activities = get_activities(trip_id)

        activity_to_edit = None

        if activity_id is not None:
            activity_to_edit = get_item_to_edit('activities', activity_id)
            if activity_to_edit is None:
                flash('Activity not found for editing.', 'error')
                return redirect(url_for('plan_trip', trip_id=trip_id))

    except Exception as e:
        print(f"Error loading trip for planning: {e}")
        flash('Error loading add activity page.', 'error')
        return redirect(url_for('view_trips'))
    
    if request.method == 'POST':
        activity_data = {
            'trip_id': trip_id,
            'activity_name': request.form.get('activity_name'),
            'activity_type': request.form.get('activity_type'),
            'activity_date': request.form.get('activity_date'),
            'activity_time': request.form.get('activity_time'),
            'location': request.form.get('location'),
            'description': request.form.get('description'),
            'cost': request.form.get('cost')
        }

        if check_date_during_trip(trip['start_date'], trip['end_date'], activity_data['activity_date']) is False:
            flash(f"Error! Please ensure the activity date is during the trip.", 'error')
            return redirect(url_for('add_activity_route', trip_id=trip_id, activity_id=activity_id))

        if activity_id is not None:
            if update_activity(activity_id, activity_data):
                flash(f"Activity '{activity_data['activity_name']}' updated successfully!", 'success')
            else:
                flash('Error updating activity. Please try again.', 'error')
            return redirect(url_for('plan_trip', trip_id=trip_id))
        
        if add_activity(activity_data):
            flash(f"Activity '{activity_data['activity_name']}' added successfully!", 'success')
        else:
            flash('Error adding activity. Please try again.', 'error')
        return redirect(url_for('plan_trip', trip_id=trip_id))

    return render_template('add_activity_route.html', trip_id=trip_id, trip=trip, activities=activities, activity_to_edit=activity_to_edit)

@app.route('/add_hotel_route/<int:trip_id>', methods=['GET', 'POST'])
@app.route('/add_hotel_route/<int:trip_id>/<int:hotel_id>', methods=['GET', 'POST'])
def add_hotel_route(trip_id, hotel_id=None):
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

        hotel_to_edit = None

        if hotel_id is not None:
            hotel_to_edit = get_item_to_edit('hotels', hotel_id)
            if hotel_to_edit is None:
                flash('Hotel not found for editing.', 'error')
                return redirect(url_for('plan_trip', trip_id=trip_id))

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
        
        if check_valid_hotel_dates(trip['start_date'], trip['end_date'], hotel_data['check_in_date'], hotel_data['check_out_date']) is True:
            hotel_data['num_days'] = number_of_days(hotel_data['check_in_date'], hotel_data['check_out_date'])

            if hotel_id is not None:
                if update_hotel(hotel_id, hotel_data):
                    flash(f"Hotel '{hotel_data['hotel_name']}' updated successfully!", 'success')
                else:
                    flash('Error updating hotel. Please try again.', 'error')
                return redirect(url_for('plan_trip', trip_id=trip_id))
            
            if add_hotel(hotel_data):
                flash(f"Hotel '{hotel_data['hotel_name']}' added successfully!", 'success')
            else:
                flash('Error adding hotel. Please try again.', 'error')
            return redirect(url_for('plan_trip', trip_id=trip_id))
        else:
            flash('Error! Check-out date cannot be before check-in date, or check-in date cannot be before today.', 'error')
            return redirect(url_for('add_hotel_route', trip_id=trip_id, hotel_id=hotel_id))
        
    return render_template('add_hotel_route.html', trip_id=trip_id, trip=trip, hotels=hotels, hotel_to_edit=hotel_to_edit)
    
@app.route('/add_extra_cost_route/<int:trip_id>', methods=['GET', 'POST'])
@app.route('/add_extra_cost_route/<int:trip_id>/<int:extra_cost_id>', methods=['GET', 'POST'])
def add_extra_cost_route(trip_id, extra_cost_id=None):
    """
    Add a new extra cost to a specific trip.
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
        
        extra_costs = get_extra_costs(trip_id)

        extra_cost_to_edit = None

        if extra_cost_id is not None:
            extra_cost_to_edit = get_item_to_edit('extra_costs', extra_cost_id)
            if extra_cost_to_edit is None:
                flash('Extra cost not found for editing.', 'error')
                return redirect(url_for('plan_trip', trip_id=trip_id))

    except Exception as e:
        print(f"Error loading trip for planning: {e}")
        flash('Error loading add extra cost page.', 'error')
        return redirect(url_for('view_trips'))
    
    if request.method == 'POST':
        extra_cost_data = {
            'trip_id': trip_id,
            'name': request.form.get('name'),
            'cost': request.form.get('cost'),
            'date': request.form.get('date'),
            'description': request.form.get('description')
        }

        if check_date_during_trip(trip['start_date'], trip['end_date'], extra_cost_data['date']) is False:
            flash(f"Error! Please ensure the extra cost date is during the trip.", 'error')
            return redirect(url_for('add_extra_cost_route', trip_id=trip_id, extra_cost_id=extra_cost_id))

        if extra_cost_id is not None:
            if update_extra_cost(extra_cost_id, extra_cost_data):
                flash(f"Extra cost '{extra_cost_data['name']}' updated successfully!", 'success')
            else:
                flash('Error updating extra cost. Please try again.', 'error')
            return redirect(url_for('plan_trip', trip_id=trip_id))
        
        if add_extra_cost(extra_cost_data):
            flash(f"Extra cost '{extra_cost_data['name']}' added successfully!", 'success')
        else:
            flash('Error adding extra cost. Please try again.', 'error')
        return redirect(url_for('plan_trip', trip_id=trip_id))

    return render_template('add_extra_cost_route.html', trip_id=trip_id, trip=trip, extra_costs=extra_costs, extra_cost_to_edit=extra_cost_to_edit)

@app.route('/add_flight_route/<int:trip_id>', methods=['GET', 'POST'])
@app.route('/add_flight_route/<int:trip_id>/<int:flight_id>', methods=['GET', 'POST'])
def add_flight_route(trip_id, flight_id=None):
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

        flight_to_edit = None

        if flight_id is not None:
            flight_to_edit = get_item_to_edit('flights', flight_id)
            if flight_to_edit is None:
                flash('Flight not found for editing.', 'error')
                return redirect(url_for('plan_trip', trip_id=trip_id))

    except Exception as e:
        print(f"Error loading trip for planning: {e}")
        flash('Error loading add flight page.', 'error')
        return redirect(url_for('plan_trip', trip_id=trip_id))

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
        
        if check_valid_flight_dates(trip['start_date'], trip['end_date'], flight_data['departure_date'], flight_data['arrival_date']) is True:
            if flight_id is not None:
                if update_flight(flight_id, flight_data):
                    flash(f"Flight '{flight_data['flight_number']}' updated successfully!", 'success')
                else:
                    flash('Error updating flight. Please try again.', 'error')
                return redirect(url_for('plan_trip', trip_id=trip_id))

            if add_flight(flight_data):
                flash(f"Flight '{flight_data['flight_number']}' added successfully!", 'success')
            else:
                flash('Error adding flight. Please try again.', 'error')
            return redirect(url_for('plan_trip', trip_id=trip_id))
        else:
            flash('Error! Arrival date cannot be before departure date, and dates must fall during the trip date period.', 'error')
            return redirect(url_for('add_flight_route', trip_id=trip_id, flight_id=flight_id))
    
    return render_template('add_flight_route.html', trip_id=trip_id, trip=trip, flights=flights, flight_to_edit=flight_to_edit)

@app.route('/weather_forecasts/<int:trip_id>', methods=['GET', 'POST'])
def trip_weather(trip_id):
    """
    Shows the weather forecast for days during a specific trip
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
        
        # Updates weather information at the end of every day
        if check_date_in_past(trip['weather_updated_at']):
            store_weather_for_trip(trip['id'], trip['destination'], trip['country'], trip['start_date'], trip['end_date'])
            update_trip_weather_date(trip_id, date.today().isoformat())

        weather_info = get_weather_info(trip_id)

    except Exception as e:
        print(f"Error loading trip for planning: {e}")
        flash('Error loading weather information page.', 'error')
        return redirect(url_for('view_trips'))

    return render_template('weather_forecasts.html', trip=trip, trip_id=trip_id, weather_info=weather_info)

@app.route('/itinerary/<int:trip_id>', methods=['GET', 'POST'])
def view_itinerary(trip_id):
    """
    Displays a detailed itinerary for a specific trip
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
        
        itinerary_groups = build_itinerary(trip_id)

    except Exception as e:
        print(f"Error loading itinerary: {e}")
        flash('Error loading itinerary.', 'error')
        return redirect(url_for('plan_trip', trip_id=trip_id))

    return render_template('itinerary.html', trip=trip, trip_id=trip_id, itinerary_groups=itinerary_groups)

@app.route('/chatbot/<int:trip_id>', methods=['GET', 'POST'])
def planner_chatbot(trip_id):
    """
    Allows users to interact with Gemini to help them plan their trip
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

    except Exception as e:
        print(f"Error loading trip for chatbot: {e}")
        flash('Error loading chatbot page.', 'error')
        return redirect(url_for('view_trips'))
    
    setup_chatbot(trip_id)

    return render_template('chatbot.html', trip_id=trip_id, trip=trip)

@app.route('/chatbot/<int:trip_id>/message', methods=['GET', 'POST'])
def chatbot_message(trip_id):
    """
    Sends the user's message to the chatbot and returns the chatbot's response
    :return: JSON response with the chatbot's reply
    """
    user_message = ""
    if request.is_json:
        user_message = request.json.get("message", "")
    else:
        user_message = request.form.get("message", "")
    return {"reply": generate_chatbot_message(trip_id, user_message)}

# --- Delete Routes ---
@app.route('/delete_trip/<int:trip_id>')
def delete_trip(trip_id):
    """
    Delete a trip and all associated records.
    :param trip_id: ID of the trip to delete
    """
    if delete_trip_and_associated_records(trip_id):
        flash('Trip and all associated records deleted successfully.', 'success')
    else:
        flash('Error deleting trip. Please try again.', 'error')

    return redirect(url_for('view_trips'))

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

@app.route('/delete_activity/<int:activity_id>/<int:trip_id>')
def delete_activity(activity_id, trip_id):
    """
    Delete an activity from a specific trip.
    :param activity_id: ID of the activity to delete
    :param trip_id: ID of the trip the activity belongs to
    """
    if delete_activity_record(trip_id, activity_id):
        flash('Activity deleted successfully.', 'success')
    else:
        flash('Error deleting activity. Please try again.', 'error')

    return redirect(url_for('plan_trip', trip_id=trip_id))

@app.route('/delete_extra_cost/<int:extra_cost_id>/<int:trip_id>')
def delete_extra_cost(extra_cost_id, trip_id):
    """
    Delete an extra cost from a specific trip.
    :param extra_cost_id: ID of the extra cost to delete
    :param trip_id: ID of the trip the extra cost belongs to
    """
    if delete_extra_cost_record(trip_id, extra_cost_id):
        flash('Extra cost deleted successfully.', 'success')
    else:
        flash('Error deleting extra cost. Please try again.', 'error')

    return redirect(url_for('plan_trip', trip_id=trip_id))

# --- Methods ---
def check_valid_trip_date(start_date, end_date):
    if validate_end_date(start_date, end_date) is True and check_date_after_today(start_date) is True:
        return True
    else:
        return False

def check_valid_flight_dates(start_date, end_date, start_date_input, end_date_input):
    """
    Validate that both start_date_input and end_date_input is between start_date and end_date
    :param start_date: String in YYYY-MM-DD format
    :param end_date: String in YYYY-MM-DD format
    :param start_date_input: String in YYYY-MM-DD format
    :param end_date_input: String in YYYY-MM-DD format
    :return: Boolean indicating if the requirements are satisfied
    """
    if check_date_during_trip(start_date, end_date, start_date_input) is True and check_date_during_trip(start_date, end_date, end_date_input) is True:
        return True
    else:
        return False
    
def check_valid_hotel_dates(start_date, end_date, start_date_input, end_date_input):
    """
    Validate that the end_date_input is after start_date_input and that both start_date_input and end_date_input is between start_date and end_date
    :param start_date: String in YYYY-MM-DD format
    :param end_date: String in YYYY-MM-DD format
    :param start_date_input: String in YYYY-MM-DD format
    :param end_date_input: String in YYYY-MM-DD format
    :return: Boolean indicating if the requirements are satisfied
    """
    if validate_end_date(start_date_input, end_date_input) is True and check_date_during_trip(start_date, end_date, start_date_input) is True and check_date_during_trip(start_date, end_date, end_date_input) is True:
        return True
    else:
        return False

def validate_end_date(start_date, end_date):
    """
    Validate that the end date is not before the start date.
    :param start_date: Start date as a string in YYYY-MM-DD format
    :param end_date: End date as a string in YYYY-MM-DD format
    :return: Boolean indicating if the end date is valid
    """
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        return end_date >= start_date
    except ValueError:
        return False

def check_date_after_today(date_input):
    """
    Validate that the given date is either today or after today
    :param date: String in YYYY-MM-DD format
    :return: Boolean indicating if the given date is today or after today
    """
    try:
        converted_date = datetime.strptime(date_input, '%Y-%m-%d').date()
        return converted_date >= date.today()
    except ValueError:
        return False

def check_date_in_past(date_input):
    """
    Checks if given date is before today
    :param date_input: String in YYYY-MM-DD format
    :return: Boolean indicating if the date is before today or not
    """
    try:
        converted_date = datetime.strptime(date_input, '%Y-%m-%d').date()
        return converted_date < date.today()
    except ValueError:
        return False

def check_date_during_trip(start_date, end_date, date_input):
    """
    Validates that date_input is between start_date and end_date (inclusive)
    :param start_date: String in YYYY-MM-DD format
    :param end_date: String in YYYY-MM-DD format
    :param date_input: String in YYYY-MM-DD format
    :return: Boolean indicating if date_input is within the start and end dates
    """
    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    date_input = datetime.strptime(date_input, '%Y-%m-%d').date()

    return start_date <= date_input <= end_date

def calculate_total_event_cost(event_list):
    """
    Calculate the total cost of a list of events (activities, flights, or extra costs).
    :param event_list: List of events with a 'cost' key
    :return: Total cost as a float
    """
    total_cost = 0.0
    for event in event_list:
        total_cost += event['cost']
    return total_cost

def calculate_hotel_total_cost(hotel_list):
    """
    Calculate the total cost of a list of hotels.
    :param hotel_list: List of hotels with 'cost_per_day' and 'num_days' keys
    :return: Total cost as a float
    """
    total_cost = 0.0
    for hotel in hotel_list:
        total_cost += hotel['cost_per_day'] * hotel['num_days']
    return total_cost

def calculate_overall_cost(trip_id):
    """
    Calculate the total cost of a trip by summing up the costs of activities, hotels, flights, and extra costs.
    :param trip_id: ID of the trip
    :return: Total cost as a float
    """
    try:
        activities = get_activities(trip_id)
        hotels = get_hotels(trip_id)
        flights = get_flights(trip_id)
        extra_costs = get_extra_costs(trip_id)

        activities_cost = calculate_total_event_cost(activities)
        hotels_cost = calculate_hotel_total_cost(hotels)
        flights_cost = calculate_total_event_cost(flights)
        extra_costs_cost = calculate_total_event_cost(extra_costs)

        total_cost = activities_cost + hotels_cost + flights_cost + extra_costs_cost
        return total_cost
    
    except Exception as e:
        print(f"Error calculating total cost: {e}")
        return 0.0

def number_of_days(start_date_str, end_date_str):
    """
    Calculate the number of days between two dates.
    :param start_date_str: Start date as a string
    :param end_date_str: End date as a string
    :return: Number of days as an integer
    """
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        delta = end_date - start_date
        return delta.days
    except ValueError:
        return 0

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

def build_itinerary(trip_id):
    """Build a date-grouped itinerary with hotels, flights, and activities."""
    trip = get_single_trip(trip_id)
    if trip is None:
        return []

    activities = get_activities(trip_id)
    hotels = get_hotels(trip_id)
    flights = get_flights(trip_id)

    entries = []

    for hotel in hotels:
        entries.append({
            'date': hotel['check_in_date'],
            'sort_time': '0:00',
            'category': 'Hotel',
            'title': hotel['hotel_name'],
            'time': f"Check-in: {hotel['check_in_date']}",
            'details': f"Location: {hotel['location'] or 'Not provided'} | Cost/day: ${float(hotel['cost_per_day'] or 0):.2f} | Nights: {hotel['num_days'] or 0} | {hotel['description'] or 'No notes'}",
        })
        entries.append({
            'date': hotel['check_out_date'],
            'sort_time': '0:00',
            'category': 'Hotel',
            'title': hotel['hotel_name'],
            'time': f"Check-out: {hotel['check_out_date']}",
            'details': f"Location: {hotel['location'] or 'Not provided'} | Cost/day: ${float(hotel['cost_per_day'] or 0):.2f} | Nights: {hotel['num_days'] or 0} | {hotel['description'] or 'No notes'}",
        })

    for flight in flights:
        entries.append({
            'date': flight['departure_date'],
            'sort_time': flight['departure_time'],
            'category': 'Flight',
            'title': f"{flight['airline']} {flight['flight_number']}",
            'time': f"Departure: {flight['departure_time'] or 'N/A'}",
            'details': f"Flight from {flight['departure_date']} to {flight['arrival_date']} | Total Cost: ${float(flight['cost'] or 0):.2f} | {flight['description'] or 'No notes'}",
        })
        entries.append({
            'date': flight['arrival_date'],
            'sort_time': flight['arrival_time'],
            'category': 'Flight',
            'title': f"{flight['airline']} {flight['flight_number']}",
            'time': f"Arrival: {flight['arrival_time'] or 'N/A'}",
            'details': f"Flight from {flight['departure_date']} to {flight['arrival_date']} | Total Cost: ${float(flight['cost'] or 0):.2f} | {flight['description'] or 'No notes'}",
        })

    for activity in activities:
        entries.append({
            'date': activity['activity_date'],
            'sort_time': activity['activity_time'],
            'category': 'Activity',
            'title': activity['activity_name'],
            'time': activity['activity_time'] or 'Time not set',
            'details': f"Type: {activity['activity_type'] or 'General'} | Location: {activity['location'] or 'Not provided'} | Cost: ${float(activity['cost'] or 0):.2f} | {activity['description'] or 'No notes'}",
        })

    entries.sort(
        key=lambda item: datetime.strptime(
            item["date"] + " " + item["sort_time"],
            "%Y-%m-%d %H:%M"
        )
    )

    grouped = {}

    for item in entries:
        date = item["date"]

        if date not in grouped:
            grouped[date] = []

        grouped[date].append(item)

    return grouped

# --- Gemini API Chatbot ---
def generate_trip_summary(trip_data):
    """
    Generates a summary of the trip
    :param trip_data: Dictionary containing all the trip's information
    :return: str
    """
    summary = f"""Here is an overview of this trip. The user is calling this trip {trip_data['trip_name']}. The user will be visiting {trip_data['destination']} which is in the country {trip_data['country']}.
                This trip lasts from {trip_data['start_date']} to {trip_data['end_date']}. The budget for this trip is {trip_data['budget']}. There are {trip_data['num_travelers']}
                people on this trip. The companions on this trip are {trip_data['companions']}. The user's description for this trip is this: {trip_data['description']}.
                """
    return summary

def generate_flights_summary(flight_data):
    """
    Generates a summary of all the user's flights
    :param flight_data: List of flights
    :return: str
    """
    if not flight_data:
        return "There are no flights currently saved"
    
    lines = []

    for flight in flight_data:
        airline = flight['airline']
        flight_number = flight['flight_number']
        departure_date = flight['departure_date']
        departure_time = flight['departure_time']
        arrival_date = flight['arrival_date']
        arrival_time = flight['arrival_time']
        cost = flight['cost']
        desciption = flight['description']
        summary = f"""The user is taking a flight with the airline {airline}. The flight number is {flight_number}. The departure date is {departure_date} and the departure time
                    is {departure_time}. The arrival date is {arrival_date} and the arrival time is {arrival_time}. The cost of this flight is ${cost}. The user wrote this
                    description: {desciption}
        """
        lines.append(summary)
    return "\n".join(lines)

def generate_hotels_summary(hotel_data):
    """
    Generates a summary of hotels for the trip
    :param hotel_data: List of hotels
    :return: str
    """
    if not hotel_data:
        return "There are no hotels currently saved."

    lines = []
    total = 0.0
    for hotel in hotel_data:
        name = hotel['hotel_name']
        check_in = hotel['check_in_date']
        check_out = hotel['check_out_date']
        cost_per_day = hotel['cost_per_day'] or 0
        num_days = hotel['num_days'] or 0
        notes = hotel['description'] or ''
        cost = (cost_per_day or 0) * (num_days or 0)
        total += cost
        lines.append(f"Hotel '{name}' from {check_in} to {check_out}, {num_days} nights at ${cost_per_day} per day (total ${cost:.2f}). Notes: {notes}")

    lines.append(f"Total hotel cost: ${total:.2f} across {len(hotel_data)} bookings.")
    return "\n".join(lines)

def generate_activities_summary(activity_data):
    """
    Generates a summary of activities for the trip
    :param activity_data: List of activities
    :return: str
    """
    if not activity_data:
        return "There are no activities currently saved."

    lines = []
    total = 0.0
    for activity in activity_data:
        name = activity['activity_name'] or ''
        atype = activity['activity_type'] or ''
        adate = activity['activity_date'] or ''
        atime = activity['activity_time'] or ''
        location = activity['location'] or ''
        cost = activity['cost'] or 0
        total += cost
        lines.append(f"Activity '{name}' ({atype}) on {adate} at {atime} in {location}. Cost: ${cost:.2f}.")

    lines.append(f"Total activities cost: ${total:.2f} across {len(activity_data)} activities.")
    return "\n".join(lines)

def generate_extra_costs_summary(extra_costs):
    """
    Generates a summary of extra costs for the trip
    :param extra_costs: List of extra cost records
    :return: str
    """
    if not extra_costs:
        return "There are no extra costs currently saved."

    lines = []
    total = 0.0
    for extra_cost in extra_costs:
        name = extra_cost['name']
        edate = extra_cost['date']
        cost = extra_cost['cost'] or 0
        desc = extra_cost['description'] or ''
        total += cost
        lines.append(f"Extra cost '{name}' on {edate}: ${cost:.2f}. {desc}")

    lines.append(f"Total extra costs: ${total:.2f} across {len(extra_costs)} items.")
    return "\n".join(lines)

def get_current_trip_context(trip_id):
    """
    Creates a string containing all current information about the trip by using latest information in database
    :param trip_id: ID of the trip
    :return: String
    """
    trip = get_single_trip(trip_id)
    flights = get_flights(trip_id)
    hotels = get_hotels(trip_id)
    activities = get_activities(trip_id)
    extra_costs = get_extra_costs(trip_id)

    trip_summary = generate_trip_summary(trip)
    flights_summary = generate_flights_summary(flights)
    hotels_summary = generate_hotels_summary(hotels)
    activities_summary = generate_activities_summary(activities)
    extra_costs_summary = generate_extra_costs_summary(extra_costs)

    context = f"""
        CURRENT TRIP INFORMATION

        Trip:
        {trip_summary}

        Flights:
        {flights_summary}

        Hotels:
        {hotels_summary}

        Activities:
        {activities_summary}

        Extra costs:
        {extra_costs_summary}
        """
    return context

def setup_chatbot(trip_id):
    """
    Sets up the initial chat history for the chatbot with a prompt and all the current trip information
    :return: None
    """
    global chat_history
    chat_history = []

    today = date.today().isoformat()

    prompt = (f"""
        You are a helpful travel planning assistant.
        Today is {today}.
        Help the user with questions about their trip.
        Use the trip information provided by the application when answering.
        If information is not available, say that you do not have that information.
        Do not use Markdown in your answers."""
    )

    context = get_current_trip_context(trip_id)

    chat_history.append({"role": "user", "parts": [{"text": prompt}]})
    chat_history.append({"role": "user", "parts": [{"text": context}]})

def generate_chatbot_message(trip_id, user_message):
    """
    Generates the chatbot's response using the user's message
    :param user_message: str
    :return: str
    """
    global chat_history
    if chat_history is None:
        chat_history = []

    message = (user_message or "").strip()

    if message == "":
        return "Please type a question or message and I'll answer about your assignments and tests."

    if not chat_history:
        setup_chatbot(trip_id)

    context = get_current_trip_context(trip_id)
    chat_history[1] = {"role": "user", "parts": [{"text": context}]}
    chat_history.append({"role": "user", "parts": [{"text": user_message}]})

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=chat_history,
    )

    chat_history.append({"role": "model", "parts": [{"text": response.text}]})

    return getattr(response, "text", "Sorry, I could not generate a response.")


if __name__ == "__main__":
    global database_name
    database_name = 'trips.db' # Set the database name

    chat_history = [] # Create empty chat history list for Gemini API to access

    first_run = True

    if (pathlib.Path.cwd() / database_name).exists():
        first_run = False
    
    if first_run:
        set_up_database() # Set up the database if it's the first run

    app.run(debug=True) # Run the flask app


# Uncomment this if you want to run the file chatbot_gemini.py
# database_name = 'trips.db'






