# Travel-Planner

A full-stack travel planning web application that helps users organize trips by managing flights, hotels, activities, expenses, and key trip details in one place. The application uses Flask and SQLite for backend logic and persistent data storage, and integrates Open-Meteo for weather forecasts. Users can also interact with a Gemini-powered AI travel assistant that uses saved trip data to provide personalized planning assistance.

## Features
* Create, view, edit, and delete trips through a full-stack web interface
* Organize flights, hotels, activities, and additional expenses for each trip
* Track key trip details including destination, travel dates, budget, travelers, and notes
* View a day-by-day itinerary that organizes flights, hotels, and activities in chronological order
* Persist trip data with SQLite, allowing information to be saved and retrieved across application sessions
* Display available upcoming weather forecasts using Open-Meteo Weather API
* Use an AI travel assistant powered by Google Gemini API that utilizes saved trip information to answer trip-specific questions

## Screenshots
### Creating a New Trip
<img src="images/create_trip.png" height="600">

### Viewing Itinerary
<img src="images/itinerary_sample.png" >

### AI Travel Assistant
<img src="images/chatbot_demo.png" height="500">

## Technologies Used
* Python
* HTML/CSS
* Flask
* Jinja
* SQLite
* Open-Mateo API
* Gemini API

## Installation
1. Clone the repository:
```
git clone https://github.com/IJustinChan/Travel-Planner.git
```

2. Navigate to the project directory:
```
cd Travel-Planner
```

3. Install the required Python packages:
```
pip install -r requirements.txt
```

## Gemini API Key Setup
This project uses the Gemini API for the AI travel assistant. You will need to get your own Gemini API key before running the application.

Please visit Google AI Studio and use your Google Account to generate your own Gemini API key: https://aistudio.google.com/

Next, set up your API key as an environment variable. Copy and paste the following line of code into the terminal to connect to Gemini API:
```
$env:GEMINI_API_KEY="your_api_key_here"
```

## Running the Program
Once you have added your API key, start the Flask application by running `main.py`. Click the link that is generated and you will be able to access the website. 

## Project Structure
```
TRAVEL-PLANNER/
├── static/
│   ├── script.js
│   └── style.css
├── templates/
│   ├── add_activity_route.html
│   ├── add_extra_cost_route.html
│   ├── add_flight_route.html
│   ├── add_hotel_route.html
│   ├── chatbot.html
│   ├── home.html
|   ├── itinerary.html
│   ├── plan.html
│   ├── trips.html
│   └── weather_forecasts.html
├── database.py
├── main.py
├── trips.db
└── weather_information.py
```
