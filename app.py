from flask import Flask, request, jsonify
import csv
import re


app = Flask(__name__)

@app.route("/slack/events", methods=["POST"])
def slack_events():
    data = request.json
     # Check if this is a challenge request
    if data.get('type') == 'url_verification':
        # Respond to the challenge
        return jsonify({
            "challenge": data.get('challenge')
        })

    # Check if this is a message from a user
    if data["type"] == "event_callback" and data["event"]["type"] == "message":
        process_message(data["event"])
    return jsonify({"status": "ok"})

def process_message(event):
    # Extract information from the event
    link = re.search("(http[s]?://[^\s]+)", event["text"]).group(0)
    sender = event["user"]
    hashtags = " ".join(re.findall("(#[^\s]+)", event["text"]))
    remaining_text = re.sub("(http[s]?://[^\s]+)|(#\S+)", "", event["text"]).strip()

    # Save to CSV
    with open("messages.csv", "a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([link, sender, hashtags, remaining_text])

if __name__ == "__main__":
    app.run(port=3000, debug=True)

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
