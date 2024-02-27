from flask import Flask, request, jsonify
import re
import requests
import os


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
    'Authorization': f'Bearer {AIRTABLE_PERSONAL_ACCESS_TOKEN}',
    'Content-Type': 'application/json',
}

def post_to_airtable(data):
    """Post the extracted data to Airtable"""
    response = requests.post(AIRTABLE_ENDPOINT, json=data, headers=headers)
    print(response.json())

@app.route('/slack/events', methods=['POST'])
def slack_events():
    data = request.json
    
    if data.get('type') == 'event_callback' and data['event'].get('type') == 'message':
        message = data['event'].get('text')
        user = data['event'].get('user')  # Consider resolving this to a username if needed
        
        # Extract information
        links = ', '.join(re.findall(r'http[s]?://\S+', message))
        hashtags = ', '.join(re.findall(r'#\w+', message))
        text = re.sub(r'(http[s]?://\S+|#\w+)', '', message).strip()
        
        # Prepare data for Airtable
        data_to_post = {
            "fields": {
                "Link": links,
                "Sender": user,  # Consider using usernames
                "Hashtags": hashtags,
                "Text": text
            }
        }
        
        # Post to Airtable
        post_to_airtable(data_to_post)
        
        return 'OK', 200
    
    return 'OK', 200

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
