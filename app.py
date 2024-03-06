import os
import re
import requests
import datetime
from flask import (Flask, redirect, render_template, request, send_from_directory, url_for)

app = Flask(__name__)

# Airtable setup
AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')

# Slack setup
SLACK_TOKEN = os.getenv('SLACK_TOKEN')  # Ensure this is set in your environment variables

# Headers for Airtable
airtable_headers = lambda token: {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json',
}

# Headers for Slack
slack_headers = {
    'Authorization': f'Bearer {SLACK_TOKEN}',
    'Content-Type': 'application/json',
}

def post_to_airtable(table_name, data):
    """Dynamically post the extracted data to the specified Airtable table"""
    AIRTABLE_PERSONAL_ACCESS_TOKEN = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
    endpoint = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{table_name}'
    response = requests.post(endpoint, json=data, headers=airtable_headers(AIRTABLE_PERSONAL_ACCESS_TOKEN))
    if response.status_code != 200:
        print(f"Error posting to Airtable: {response.status_code}, {response.text}")
    else:
        print("Successfully posted to Airtable:", response.json())


def get_username(user_id):
    """Retrieve username from user ID using Slack API"""
    response = requests.get(f'https://slack.com/api/users.info?user={user_id}', headers=slack_headers)
    user_info = response.json()
    if response.status_code == 200 and user_info.get('ok'):
        return user_info['user']['name']
    else:
        return user_id  # Return user ID if unable to fetch username

@app.route('/slack/events', methods=['POST'])
def slack_events():
    data = request.json
    if data.get('type') == 'event_callback' and data['event'].get('type') == 'message':
        # Extract necessary information
        message = data['event'].get('text')
        user_id = data['event'].get('user')
        username = get_username(user_id)
        timestamp = data['event'].get('ts')
        date = datetime.datetime.fromtimestamp(float(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
        channel_id = data['event'].get('channel')

        # Retrieve channel information using Slack API
        response = requests.get(f'https://slack.com/api/conversations.info?channel={channel_id}', headers=slack_headers)
        channel_info = response.json()
        print(f'Channel info: {channel_info}')
        if response.status_code == 200 and channel_info.get('ok'):
            channel_name = channel_info['channel']['name']
            # Extract information, adjust regex to account for angle brackets
            links = ', '.join(re.findall(r'<(http[s]?://\S+)>', message))
            hashtags = ', '.join(re.findall(r'#\w+', message))
            text = re.sub(r'(<http[s]?://\S+>|#\w+)', '', message).strip()
            
            # Prepare data for Airtable
            data_to_post = {
                "fields": {
                    "Link": links,
                    "Sender": username,
                    "Hashtags": hashtags,
                    "Text": text,
                    "Date": date,
                    "Channel": channel_name
                }
            }
            print(f'Extracted data: {data_to_post}')
            
            # Check if the channel is one of the specified ones before posting
            if channel_name.lower() in ['projects', 'research']:  # Add more channel names as needed
                post_to_airtable(channel_name, data_to_post)
                print(f'Posted to Airtable: {data_to_post}')
        
        return 'OK', 200
    
    return 'OK', 200



@app.route('/')
def index():
   print('Request for index page received')
   return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/hello', methods=['POST'])
def hello():
   name = request.form.get('name')

   if name:
       print('Request for hello page received with name=%s' % name)
       return render_template('hello.html', name = name)
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))
if __name__ == '__main__':
    app.run(debug=True, port=5000)


# import os

# from flask import (Flask, redirect, render_template, request,
#                    send_from_directory, url_for)

# app = Flask(__name__)


# @app.route('/')
# def index():
#    print('Request for index page received')
#    return render_template('index.html')

# @app.route('/favicon.ico')
# def favicon():
#     return send_from_directory(os.path.join(app.root_path, 'static'),
#                                'favicon.ico', mimetype='image/vnd.microsoft.icon')

# @app.route('/hello', methods=['POST'])
# def hello():
#    name = request.form.get('name')

#    if name:
#        print('Request for hello page received with name=%s' % name)
#        return render_template('hello.html', name = name)
#    else:
#        print('Request for hello page received with no name or blank name -- redirecting')
#        return redirect(url_for('index'))


# if __name__ == '__main__':
#    app.run()
