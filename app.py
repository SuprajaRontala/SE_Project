import datetime
from flask import *
import pywhatkit
import requests
import wikipedia
import pyjokes 
app = Flask(__name__)

@app.route('/')
def index():
    print("hello")
    return render_template('index.html')

@app.route('/templates/<path:filename>')
def download_file(filename):
    return send_from_directory('templates/', filename)
# Define the route to process voice commands

@app.route('/process-command', methods=['POST'])

def process_command():
    print("hello")
    data = request.get_json()
    command = data.get('command', 'No command provided')
    if data is None:
        return jsonify({'error': 'Invalid JSON data.'}), 400
    response = ""
    print(command)
    # Process the command based on keywords
    if 'hello' in command:
        response = greeting_message()

    elif 'play music' in command:
        print("song")
        response = command_play_music(command=command)

    elif 'time' in command:
        response = command_get_current_time()

    elif 'who is' in command:
        response = command_search_wikipedia(command)

    elif 'joke' in command:
        response = command_tell_joke()

    elif 'tell me news' in command:
        response = command_tell_news()
    else:
        response = "Sorry, I couldn't understand you, please speak again with any of the following keywords: hello, music, time, who is, joke, news "
    return jsonify({'response': response})

def greeting_message():
    hour = int(datetime.datetime.now().hour)

    if hour >= 0 and hour < 12:
        return "Good Morning! I am Braille Bot, your Voice Assistant. How can I assist you?"

    elif hour >= 12 and hour < 18:
        return "Good Afternoon! I am Braille Bot, your Voice Assistant. How can I assist you?"
    else:
        return "Good Evening! I am Braille Bot, your Voice Assistant. How can I assist you?"
    
def command_play_music(command):
    command = command.replace('play music', '')
    print(command)
   try:

        url = pywhatkit.playonyt(command, open_video=True)
        url = url.split('?v=')[1].split('/')[0]
        url = f"https://www.youtube.com/embed/{url}?autoplay=1&mute=1"
        # Check if the URL is valid by making a request
        response = requests.get(url)
        if response.status_code == 200:
            return url
        else:
            return " "
    except Exception as e:
        return "An error occurred while trying to play the music.Please provide another music"

def command_get_current_time():
    time = datetime.datetime.now().strftime('%I:%M %p')

    if not time:

        return "Sorry, I am unable to tell the time."

    return f"The current time is {time}"

def command_search_wikipedia(command):
    person = command.replace('who is', '').strip()

    try:
        response = requests.get(f"https://en.wikipedia.org/w/api.php?action=query&format=json&list=search&utf8=1&srsearch={person}")
        response.raise_for_status()
        data = response.json()
        if 'query' in data and 'search' in data['query']:
            if data['query']['search']:
                # Get the summary from the first search result
                info = wikipedia.summary(data['query']['search'][0]['title'], sentences=4)
                return info
            else:
                return f"No results found for {person}. Please try another query."
        info = wikipedia.summary(person, sentences=4)
        return info

    except wikipedia.exceptions.DisambiguationError as e:
        return f"Multiple results found for {person}. Please provide more specific input."
def command_tell_joke():
    jokes_api = "https://icanhazdadjoke.com/slack"
    response = requests.get(jokes_api)
    
    if response.status_code == 200:
        joke = response.json()['attachments'][0]['text']
        if joke:
            return joke
        
    else:
        raise Exception(f"Failed to retrieve a joke due to the Status code: {response.status_code}")
  
command_tell_news():
    try:
        url = ('https://newsapi.org/v2/top-headlines?'
            'country=us&'
            'apiKey=13233a39c12b47e085c6aa914b4ee10f')
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            # Simulate a response with an unexpected structure
            headlines = data['invalid_key']['title']
            return "Here are the latest news headlines: " + headlines
        else:
            return "Sorry, I am unable to tell the news at the moment."

    except requests.exceptions.RequestException as e:
        return f"An error occurred while fetching news: {e}"
if __name__ == '_main_':
    app.run(debug=True)  

