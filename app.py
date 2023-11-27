import datetime
from flask import *
import pywhatkit
import requests
import wikipedia
import pyjokes
import pytz
import geopy.distance
from geopy.geocoders import Nominatim
import re
from validate_email_address import validate_email
from email.message import EmailMessage
import ssl
import smtplib
from PyMultiDictionary import MultiDictionary
dictionary = MultiDictionary()

GEOAPIFY_API_KEY = 'bad2ec3ffa3743b28a768ef23faad806'

email_sender = 'braillebotuser@gmail.com'
email_password = 'kalz qubc pnvs ecwe'
email_receiver = 'sample4123@gmail.com'

subject = 'Test mail'
app = Flask(__name__)

def render_ind():

    return render_template('index.html')

 

@app.route('/')

def index():

    return render_ind()

@app.route('/templates/<path:filename>')
def download_file(filename):
    return send_from_directory('templates/', filename)
# Define the route to process voice commands

@app.route('/process-command', methods=['POST'])

def process_command():
    data = request.get_json()
    if data is None:
        return jsonify({'error': 'Invalid JSON data.'}), 400
 
    command = data.get('command', 'No command provided')
 
    if 'hello' in command:
        return jsonify({'response': greeting_message()})
 
    if 'music' in command:
        return jsonify({'response': command_play_music(command=command)})
 
    if 'time' in command:
        return jsonify({'response': command_get_current_time()})
 
    if 'who is' in command:
        return jsonify({'response': command_search_wikipedia(command)})
 
    if 'joke' in command:
        return jsonify({'response': command_tell_joke()})
 
    if 'news' in command:
        return jsonify({'response': command_tell_news()})
    if 'nearby motels' in command:
        return jsonify({'response': get_nearby_places_accomodation(data)})
    
    if 'nearby markets'  in command:
        return jsonify({'response': get_nearby_places_commercial(data)})
    
    if 'nearby healthcare'  in command:
        return jsonify({'response': get_nearby_places_healthcare(data)})
    
    if 'nearby restaurants'  in command:
        return jsonify({'response': get_nearby_places_restaurant(data)})

    if 'define' in command:
        return jsonify({'response': get_meaning(command)})
    if 'email' in command.split():
        print(command)
        return jsonify({'response': command_send_email(command)})
 
    return jsonify({'response': "Please provide a valid input"})



def greeting_message():
    hour = int(datetime.datetime.now().hour)

    if hour >= 0 and hour < 12:
        return "Good Morning! I am Braille Bot, your Voice Assistant. How can I assist you?"

    elif hour >= 12 and hour < 18:
        return "Good Afternoon! I am Braille Bot, your Voice Assistant. How can I assist you?"
    else:
        return "Good Evening! I am Braille Bot, your Voice Assistant. How can I assist you?"

def command_play_music(command):
    video_url = extract_youtube_url(command)
    
    if video_url:
        return video_url
    else:
        return "An error occurred while trying to play the music. Please provide another music"

def extract_youtube_url(command):
    try:
        video_id = get_youtube_video_id(command)
        if video_id:
            return f"https://www.youtube.com/embed/{video_id}?autoplay=1&mute=1"
    except Exception as e:
        pass

    return None

def get_youtube_video_id(command):
    command = command.replace('play music', '').strip()
    url = pywhatkit.playonyt(command, open_video=True)
    video_id = url.split('?v=')[1].split('/')[0]
    return video_id

def command_get_current_time(date_format='%I:%M %p %Y-%m-%d', timezone_format='%H:%M:%S %Z'):
    try:
        utc_time = datetime.datetime.now(pytz.utc)
        formatted_time_with_timezone = utc_time.strftime(timezone_format)
        formatted_timestamp = datetime.datetime.now().strftime(date_format)
        return f"The current time with date: {formatted_timestamp}. with time zone offset is {formatted_time_with_timezone}."
    except Exception as e:
        return f"An error occurred: {str(e)}"

def search_wikipedia(query):
    try:
        response = requests.get(f"https://en.wikipedia.org/w/api.php?action=query&format=json&list=search&utf8=1&srsearch={query}")
        response.raise_for_status()
        data = response.json()
        
        assert 'query' in data and 'search' in data['query'], "Invalid response from Wikipedia API"
        
        if data['query']['search']:
            # Get the summary from the first search result
            info = wikipedia.summary(data['query']['search'][0]['title'], sentences=4)
            return info
        else:
            return f"No results found for {query}. Please try another query."
        
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple results found for {query}. Please provide more specific input."

def command_search_wikipedia(command):
    query = command.replace('who is', '').strip()
    return search_wikipedia(query)

def command_tell_joke():
    jokes_api = "https://icanhazdadjoke.com/slack"
    response = requests.get(jokes_api)
    
    status_code = response.status_code
    joke_data = response.json()
    
    if status_code != 200:
        raise Exception(f"Failed to retrieve a joke due to the Status code: {status_code}")
    
    joke = joke_data['attachments'][0]['text']
    
    if joke:
        return joke
def command_tell_news():
    try:
        url = ('https://newsapi.org/v2/top-headlines?'
               'country=us&'
               'apiKey=13233a39c12b47e085c6aa914b4ee10f')
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            articles = data.get('articles', [])  # Use .get() to avoid key errors
            headlines = []
            for article in articles:
                headlines.append(article.get('title', 'No Title Available'))
            return "Here are the latest news headlines: " + ", ".join(headlines)
        else:
            return "Sorry, I am unable to tell the news at the moment."

    except requests.exceptions.RequestException as e:
        return f"An error occurred while fetching news: {e}"
 def get_nearby_places_accomodation(data):
   
    lat = data['latitude'].rstrip()
    lon = data['longitude'].rstrip()

    print(lat, lon)

    
    places_url = 'https://api.geoapify.com/v2/places'
    params = {
        'categories': 'accommodation',
        #'categories': 'amenity.toilet,building.toilet,catering.restaurant,commercial.food_and_drink,catering.fast_food',
        'conditions': 'access',
        'filter': f'circle:{lon},{lat},5000',
        'filter': f'circle:{lon},{lat},5000',
        'bias': f'proximity:{lon},{lat}',
        'lang': 'en',
        'limit': 5,
        'apiKey': GEOAPIFY_API_KEY
    }
    places_data = requests.get(places_url, params=params).json()
    
    print(places_data)
    place_names = []
    for feature in places_data.get('features', []):
        try:
            place_names.append(feature['properties']['name'])
        except KeyError:
            pass

    print(place_names)
    return place_names
def get_nearby_places_restaurant(data):
   
    lat = data['latitude'].rstrip()
    lon = data['longitude'].rstrip()

    print(lat, lon)

    
    places_url = 'https://api.geoapify.com/v2/places'
    params = {
        'categories': 'catering.restaurant,commercial.food_and_drink,catering.fast_food',
        #'categories': 'amenity.toilet,building.toilet,catering.restaurant,commercial.food_and_drink,catering.fast_food',
        'conditions': 'access',
        'filter': f'circle:{lon},{lat},5000',
        'filter': f'circle:{lon},{lat},5000',
        'bias': f'proximity:{lon},{lat}',
        'lang': 'en',
        'limit': 5,
        'apiKey': GEOAPIFY_API_KEY
    }
    places_data = requests.get(places_url, params=params).json()
    
    print(places_data)
    place_names = []
    for feature in places_data.get('features', []):
        try:
            place_names.append(feature['properties']['name'])
        except KeyError:
            pass

    print(place_names)
    return place_names
def get_nearby_places_healthcare(data):
    
    lat = data['latitude'].rstrip()
    lon = data['longitude'].rstrip()

    print(lat, lon)

    
    places_url = 'https://api.geoapify.com/v2/places'
    params = {
        'categories': 'healthcare',
        #'categories': 'amenity.toilet,building.toilet,catering.restaurant,commercial.food_and_drink,catering.fast_food',
        'conditions': 'access',
        'filter': f'circle:{lon},{lat},5000',
        'filter': f'circle:{lon},{lat},5000',
        'bias': f'proximity:{lon},{lat}',
        'lang': 'en',
        'limit': 5,
        'apiKey': GEOAPIFY_API_KEY
    }
    places_data = requests.get(places_url, params=params).json()
    
    print(places_data)
    place_names = []
    for feature in places_data.get('features', []):
        try:
            place_names.append(feature['properties']['name'])
        except KeyError:
            pass

    print(place_names)
    return place_names
def get_nearby_places_commercial(data):
    
    lat = data['latitude'].rstrip()
    lon = data['longitude'].rstrip()

    print(lat, lon)

    
    places_url = 'https://api.geoapify.com/v2/places'
    params = {
        'categories': 'commercial.supermarket',
        #'categories': 'amenity.toilet,building.toilet,catering.restaurant,commercial.food_and_drink,catering.fast_food',
        'conditions': 'access',
        'filter': f'circle:{lon},{lat},5000',
        'filter': f'circle:{lon},{lat},5000',
        'bias': f'proximity:{lon},{lat}',
        'lang': 'en',
        'limit': 5,
        'apiKey': GEOAPIFY_API_KEY
    }
    places_data = requests.get(places_url, params=params).json()
    
    print(places_data)
    place_names = []
    for feature in places_data.get('features', []):
        try:
            place_names.append(feature['properties']['name'])
        except KeyError:
            pass

    print(place_names)
    return place_names

def get_meaning(command):
    
    if command.lower().startswith('define '):
        
        word_to_define = command[7:].strip()

        
        meaning_result = dictionary.meaning('en', word_to_define)

        if meaning_result:
           
            word_type, word_meaning, _ = meaning_result

            
            meaning = f'{word_to_define.capitalize()} ({word_meaning} '
            return meaning
        
    else:
        return 'Invalid command. Please use the format: Define [word]'
def is_valid_email(email):
    return validate_email(email)

def command_send_email(command):
    try:
        print(command)
        # Collect email information from the user
        to_address = command.split('to')[1].split('subject')[0].strip().lower()
        to_address = to_address.replace(' ', '').replace('attherateof', '@').replace('at', '@').replace('attherate', '@')
        if not is_valid_email(to_address):
            return "No user found. Please provide a valid Gmail address."
        from_address = email_sender
        subject = command.split('subject')[1].split('body')[0].strip()
        body = command.split('body')[1].strip()
        print(to_address, from_address, subject, body)
        
       
        message = EmailMessage()
        message['From'] = from_address
        message['To'] = to_address
        message['Subject'] = subject

        # Attach the body to the email
        message.set_content(body)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as server:
            server.login(email_sender, email_password)
            server.send_message(message)
            return "Email sent successfully!"
    except Exception as e:
        return f"An error occurred while sending the email: Please send email in the format send email to reciepient address subject content body content"

if __name__ == '_main_':
    app.run(debug=True)
