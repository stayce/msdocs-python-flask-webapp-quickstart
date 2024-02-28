import os
import re
import requests
import datetime
from flask import (Flask, redirect, render_template, request, jsonify, send_from_directory, url_for)

app = Flask(__name__)

# Airtable setup
AIRTABLE_BASE_ID = 'applUHGDLKLaRM65V'
AIRTABLE_TABLE_NAME = 'Projects'

# Assuming 'AIRTABLE_PERSONAL_ACCESS_TOKEN', 'AIRTABLE_BASE_ID', 'AIRTABLE_TABLE_NAME'
# are set as App Service settings
AIRTABLE_PERSONAL_ACCESS_TOKEN = os.getenv('AIRTABLE_PERSONAL_ACCESS_TOKEN')
# AIRTABLE_BASE_ID = os.getenv('AIRTABLE_BASE_ID')
# AIRTABLE_TABLE_NAME = os.getenv('AIRTABLE_TABLE_NAME')
AIRTABLE_ENDPOINT = f'https://api.airtable.com/v0/{AIRTABLE_BASE_ID}/{AIRTABLE_TABLE_NAME}'

headers = {
    'Authorization': f'Bearer {"patj0zu2UFayFZSF1.dfeb1e15ed875fbd349355d7512ec24f875e4c2f7523ac79f9a0f249cd2da321"}',
    'Content-Type': 'application/json',
}

def post_to_airtable(data):
    """Post the extracted data to Airtable"""
    response = requests.post(AIRTABLE_ENDPOINT, json=data, headers=headers)
    print(response.json())

# Function to get username from user ID using Slack API
def get_username(user_id):
    response = requests.get(f'https://slack.com/api/users.info?user={user_id}', headers=headers)
    user_info = response.json()
    if response.status_code == 200 and user_info['ok']:
        return user_info['user']['name']
    else:
        return None

@app.route('/slack/events', methods=['POST'])
def slack_events():
    data = request.json
    
    if data.get('type') == 'event_callback' and data['event'].get('type') == 'message':
        message = data['event'].get('text')
        user_id = data['event'].get('user')
        username = get_username(user_id)
        timestamp = data['event'].get('ts')
        date = datetime.datetime.fromtimestamp(float(timestamp)).strftime('%Y-%m-%d %H:%M:%S')
        channel_id = data['event'].get('channel')

        # Retrieve channel information using Slack API
        response = requests.get(f'https://slack.com/api/conversations.info?channel={channel_id}', headers=headers)
        channel_info = response.json()
        if response.status_code == 200 and channel_info['ok']:
            channel_name = channel_info['channel']['name']
        else:
            channel_name = "None"
        
        # Extract information
        links = ', '.join(re.findall(r'http[s]?://\S+', message))
        hashtags = ', '.join(re.findall(r'#\w+', message))
        text = re.sub(r'(http[s]?://\S+|#\w+)', '', message).strip()
        
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
        
        # Post to Airtable
        post_to_airtable(data_to_post)
        
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
