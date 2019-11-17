# Python libraries that we need to import for our bot
import random
from flask import Flask, request
from pymessenger.bot import Bot
import requests
import itertools
import passwords

app = Flask(__name__)
ACCESS_TOKEN = passwords.ACCESS_TOKEN
VERIFY_TOKEN = passwords.VERIFY_TOKEN
bot = Bot(ACCESS_TOKEN)


# We will receive messages that Facebook sends our bot at this endpoint
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook."""
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    # if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    # Facebook Messenger ID for user so we know where to send response back to
                    recipient_id = message['sender']['id']
                    if message['message'].get('text'):
                        response_sent_text = get_message(message['message']['text'])
                        send_message(recipient_id, response_sent_text)
                    # if user sends us a GIF, photo,video, or any other non-text item
                    if message['message'].get('attachments'):
                        response_sent_nontext = get_message()
                        send_message(recipient_id, response_sent_nontext)
    return "Message Processed"


def verify_fb_token(token_sent):
    # take token sent by facebook and verify it matches the verify token you sent
    # if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


# chooses a random message to send to the user
def get_message(message_text):
    message_text = message_text.lower().strip()
    hackathons = get_hackathons()
    if "next" in message_text and "hackathon" in message_text and "when" in message_text:

        return "The next hackathon is " + str(hackathons[5][1]) + " on " + str(hackathons[5][5])
    # return selected item to the user
    hackathon_name = None
    hackathon_number = -1
    for i in range(0, len(hackathons)):
        if len(hackathons[i]) == len(hackathons[3]):
            name = hackathons[i][1].strip().split(" ")[0:-1]
            name_text = ""
            for word in name:
                name_text += word + " "
            hackathon_names = name_text.strip()
            if hackathon_names in message_text and len(hackathon_names)>4:
                hackathon_name = hackathon_names
                hackathon_number = i
                break
    if hackathon_name != None:
        if "when" in message_text and "is" in message_text:
            return hackathon_name +" next happens on the " + hackathons[i][5]


# uses PyMessenger to send response to user
def send_message(recipient_id, response):
    # sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"

def get_hackathons():
    r = requests.get('https://raw.githubusercontent.com/HHEU/wiki/master/docs/index.md')
    f = open("hackathons.txt", "wb")
    f.write(r.content)
    f.close()

    hackathons = []
    f = open("hackathons.txt", "r")
    save = False
    for line in f:
        if "# Events" in line:
            save=True
        if '# Past Events' in line:
            save = False
        if save:
            hackathon = line.lower().split("|")
            hackathons.append(hackathon)
    f.close()
    return hackathons

if __name__ == "__main__":
    hackathons = get_hackathons()
    name = hackathons[6][1].strip().split(" ")[0:-1]
    name_text =""
    for word in name:
        name_text += word +" "
    hackathon_name = name_text.strip()
    print(get_message("When is IC Hacks"))
    app.run()