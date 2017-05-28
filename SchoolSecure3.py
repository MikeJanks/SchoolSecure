# --------------------------------------------------
# version py 3
# --------------------------------------------------
import time
import threading
import datetime
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

app = Flask(__name__)

account_sid = 'xxxxxxxxxx'
auth_token  = 'xxxxxxxxxx'
twilioPhoneNumber = '+17324083945'

client = Client(account_sid, auth_token)

contacts = {}  # K = phone V = username
admin = None
notifications = {}

@app.route('/sms', methods=['POST'])
def sms():

    global twilioPhoneNumber
    global admin

    number = request.form['From']  # Senders number
    message_body = request.form['Body'].strip()  # Senders message

    resp = MessagingResponse()  # stores response for sender

    # adds people into the dictionary(database)
    if number not in contacts.keys():
        # checks to see if dict is empty for admin
        if len(contacts) == 0:
            admin = number
            client.messages.create(to=admin, from_=twilioPhoneNumber, body="For admin options text 'options'")
        contacts[number] = message_body  # store a new user to dictionary

        # Notifies admin that new user has been added
        if number is not admin:
            client.messages.create(to=admin, from_=twilioPhoneNumber, body=str(contacts[number]) + " has been added")
        resp.message("You've been added to {}'s class chat as {}".format(contacts[admin],
                                                                         contacts[number]))  # response back to sender
        return str(resp)

    if number == admin:  # checks if number is admin
        respNum = None
        nameLength = None

        # chacks for special charcter for personal messages to students
        if message_body[0] == '@':
            bodyfromtext = message_body.split()
            name = bodyfromtext[0][1:]
            nameLength = len(name) + 1
            # finds student based on name
            for tempNum in contacts:
                if name.lower() == contacts[tempNum].lower():
                    respNum = tempNum
            # if name isn't found
            if respNum is None:
                resp.message("name not found")
                return str(resp)
            messageBody = " ".join(bodyfromtext)
            client.messages.create(to=respNum, from_=twilioPhoneNumber, body=messageBody[nameLength:])

        elif message_body[0] == '#':
            dateandtime(message_body)

        elif message_body.lower() == 'options':
            resp.message("These are all your options as admin:\n\n" +
                         "''@'': direct message to student by username ex:\n" +
                         "@Jon Keep up the good work.\n\n" +
                         "''#'': sets notifications,(!)-optional for immediate notification along with setting the notification ex:\n" +
                         "#4/23/2017(!) Important notice!\n\n" +
                         "''Users'': lists usernames of students in the class\n\n" +
                         "''reset'': resets admin and contacts\n(Beware! Notifications will not be reset!)")
            return str(resp)

        elif message_body.lower() == 'users':
            emptyString = ''
            for k in contacts:
                if k == admin:
                    continue
                else:
                    emptyString += contacts[k] + '\n'
