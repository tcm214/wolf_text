#! python3
from flask import Flask, request, redirect
from twilio.twiml.messaging_response import MessagingResponse
import shelve
import re

# Download the helper library from https://www.twilio.com/docs/python/install
#https://www.twilio.com/console/phone-numbers/incoming
#https://ngrok.com/docs
#C:\Users\tcm21\Downloads\ngrok-stable-windows-amd64\ngrok http 8000
#python C:\Users\tcm21\Anaconda3\Scripts\wolf_text\send_sms.py

'''
run the ngrok, update the twilio page, then the flask script. 
start game - "wolf [4 letter string representing the order of wolf on the 1st hole]"
update scores - "[letters for each player who won points that whole]""
push - "push"
end game - "done"
'''

app = Flask(__name__)

@app.route("/sms", methods=['GET', 'POST'])
def incoming_sms():
    """Send a dynamic reply to an incoming text message"""
    # Get the message the user sent our Twilio number
    body = request.values.get('Body', None)

    #resp = testfunction(body)
    resp = process_sms(body)
    # Start our TwiML response    

    return str(resp)
'''
def testfunction(body):
    resp = MessagingResponse()

    # Determine the right reply for this message

    d = shelve.open("wolf")
    d['test'] = 123
    d.close()

    if body.lower() == 'hello':
        resp.message("Hi!")
    elif body.lower() == 'bye':
        resp.message("Goodbye")

    return resp
'''

def process_sms(body):
    # Start our TwiML response
    resp = MessagingResponse()
    # Determine the right reply for this message
    body_array = body.lower().split()
    print(body_array)
    if len(body_array) != 1:
        if (('wolf' in body_array) and (re.search(r'\b[a-z]{4}\b', body_array[-1]))):
            resp = start_wolf(resp, body_array[-1])
        else:
            resp.message('error. no updates made')
    else:
        #text "done" to end the game
        if body_array[0] in ['done']: # text: "done"
            resp = end_game(resp)
        #text "push" when we push
        elif body_array[0] == 'push':# text: "push"
            resp = push_scores(resp)
        elif body_array[0].isalpha():
            try:
                for player in body_array[0]:
                    d = shelve.open("wolf") # open shelve
                    if player not in d['order']: #make sure all the entries in the score update are valid
                        resp.message('invalid player(s)')
                        break
                    d.close()
                resp = update_scores(resp, body_array[0]) #text "[letter for each player who won a point]""
            except KeyError:
                resp.message('invalid entry')#.message('invalid player(s)')
        else:
            resp.message('invalid entry')

    return resp

def start_wolf(resp, players):
    d = shelve.open("wolf")
    d['order'] = players
    d['hole value'] = 1
    d['hole number'] = 1
    for player in players:
        d[player] = 0
    
    resp.message('BEGIN GAME\n{}\n{}\n{}\n{} - wolf'.format(d['order'][0], d['order'][1], d['order'][2], d['order'][3]))
    d.close()
    return resp


def update_scores(resp, update):
    d = shelve.open("wolf")
    if len(update) == 1:
        d[update] += d['hole value']*3
    else:
        for player in update:
            d[player] += d['hole value']
    d['hole value'] = 1
    d['hole number'] += 1
    
    d.close()
    resp = scoreboard(resp)
    return resp

def push_scores(resp):
    d = shelve.open("wolf")
    d['hole value'] += 1
    d['hole number'] += 1
    d.close()
    resp = scoreboard(resp)
    return resp

def scoreboard(resp): # rotate wolf order and print order/scores
    d = shelve.open("wolf")
    temp = d['order']
    temp = temp[-1] + temp[:-1]
    d['order'] = temp

    resp.message('HOLE {}\n{} - {}\n{} - {}\n{} - {}\n{} - {} - W'.format(d['hole number'],d['order'][0], d[d['order'][0]], d['order'][1], d[d['order'][1]], d['order'][2], d[d['order'][2]], d['order'][3], d[d['order'][3]]))#.message()
    d.close()
    return resp

def final_scoreboard(resp): # rotate wolf order and print order/scores
    d = shelve.open("wolf")
    resp.message('FINAL SCOREBOARD\n{} - {}\n{} - {}\n{} - {}\n{} - {}'.format(d['order'][0], d[d['order'][0]], d['order'][1], d[d['order'][1]], d['order'][2], d[d['order'][2]], d['order'][3], d[d['order'][3]]))#.message()
    d.close()
    return resp

def end_game(resp):    
    resp = final_scoreboard(resp)
    d = shelve.open("wolf")
    d.clear()
    d.close()
    return resp


if __name__ == "__main__":
    app.run(debug=True, port=8000)
