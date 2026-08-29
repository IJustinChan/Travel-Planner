from google import genai
from main import get_single_trip, get_flights, get_hotels, get_activities, get_extra_costs
from datetime import date

client = genai.Client(api_key="YOUR_API_KEY")

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
    message = (user_message or "").strip()

    if message == "":
        return "Please type a question or message and I'll answer about your assignments and tests."

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
    chat_history = []
    setup_chatbot(7)
    print(generate_chatbot_message(7, "Hello. What day is it today? Tell me about my trip, flights, hotels, activities, and extra costs. How much dollars is the extra cost gfd? Which city am I going to?"))

