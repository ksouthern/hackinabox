# Python libraries that we need to import for our bot
import random
from flask import Flask, request
from pymessenger.bot import Bot
import requests
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
    if "next" in message_text and "hackathon" in message_text and "when" in message_text:
        hackathons = get_hackathons()
        return "The next hackathon is " + str(hackathons[5][1]) + " on " + str(hackathons[5][5])
    # return selected item to the user
    else:
        return "Hey"


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
        if save:
            hackathon = line.split("|")
            hackathons.append(hackathon)
    f.close()
    return hackathons

if __name__ == "__main__":
    app.run()