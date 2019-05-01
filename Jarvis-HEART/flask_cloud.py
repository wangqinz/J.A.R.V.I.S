from flask import Flask, request
import json, os, logging
import time as t
import requests
from datetime import datetime
from multiprocessing import Process
from configparser import ConfigParser

from rasa_nlu.model import Metadata, Interpreter
from rasa_nlu import config
from rasa_nlu.model import Trainer
from rasa_core.agent import Agent
from rasa_core.interpreter import RasaNLUInterpreter

from bot import *
#### api loading
import sys
sys.path.insert(0, 'api_supports/')
from weatherAPI import *
from twitchAPI import *
from reminderAPI import *
from bridge import *

############# fb credential data #################
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
fb_verify = None
fb_secret = None
page_id = None
fb_access_token = None
##################################################
############# global data structure ##############
agent = None
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
##level:  DEBUG, INFO, WARNING, ERROR, CRITICAL
handler = logging.FileHandler('jarvis_fail.log')
handler.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s : %(message)s')
handler.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(handler)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)
##################################################

app = Flask(__name__)

@app.route('/', methods=['GET'])
def handle_verification():
	logger.info("Handling Verification.")
	if request.args.get('hub.verify_token', '') == fb_verify:
		logger.debug("Verification successful!")
		return request.args.get('hub.challenge', '')
	else:
		logger.debug("Verification failed!")
		return 'Error, wrong validation token'

@app.route('/webhook', methods=['POST'])
def handle_messages():
	payload = request.get_data()
	print(request)
	for sender, message in messaging_events(payload):
		logger.info("Incoming from %s: %s" % (sender, message))
		if message == None:
			logger.error("wrong request format >> %s",str(payload,'utf-8'))
			return "fail"
		else:
			response = agent.handle_message(message)
			if len(response) == 0:
				logger.error("api error >> %s",{'req':message})
				res = "sry, my mind is a bit of mess right now :("
				send_message(fb_access_token, sender, res.encode('unicode_escape'))
				return "error"
			else:
				response = response[0]['text']
			logger.info(response)
			## decode response  
			if "apiCall$%$" in response:
				response = response.split("$%$")[1]
				jsonDec = json.decoder.JSONDecoder()
				params = jsonDec.decode(response)
				## append sender info as well as token \
				params['fb_access_token'] = fb_access_token
				params['sender'] = sender

				res = deliver_tasks(params)
				if res['err'] != None:
					logger.error("api error >> %s",{'mes':message,'req':params,'res':res['err']})
				else:
					logger.info(res)
				send_message(fb_access_token, sender, res['msg'].encode('unicode_escape'))
			else:
				## not api call simply return
				if "sry, I can't understand" in response or "sorry" in response:
					logger.warn("invalid recognization >> %s",{'from':sender,'input': message})
				send_message(fb_access_token, sender, response.encode('unicode_escape'))

			# if len(response) == 0:
			# 	logger.error("api error >> %s",{'req':message})
			# 	res = "sry, my mind is a bit of mess right now :(".encode('unicode_escape')
			# else:
			# 	content = response[0]['text']
			# 	if "$$reminder" in content:


			# 	res = content.encode('unicode_escape')
			

			# 	send_message(fb_access_token, sender, res)
	return "ok"

def messaging_events(payload):
	"""
	Generate tuples of (sender_id, message_text) from the
	provided payload.
	"""
	data = json.loads(str(payload,'utf-8'))
	messaging_events = data["entry"][0]["messaging"]
	for event in messaging_events:
		if "message" in event and "text" in event["message"]:
			yield event["sender"]["id"], event["message"]["text"]
		else:
			yield event["sender"]["id"], None



def send_message(token, recipient, text):
	"""Send the message text to recipient with id recipient.
	"""
	r = requests.post("https://graph.facebook.com/v2.6/me/messages",
	params={"access_token": token},
	data=json.dumps({
	  "recipient": {"id": recipient},
	  "message": {"text": text.decode('unicode_escape')}
	}),
	headers={'Content-type': 'application/json'})
	if r.status_code != requests.codes.ok:
		logger.warn("error happens when sending back request >> %s",r.text)



if __name__ == '__main__':
	config = ConfigParser()
	config.read(os.path.join(BASE_DIR, 'fbconfig.ini'))
	fb_verify = config.get("fb_credential", "fb_verify")
	fb_secret = config.get("fb_credential", "fb_secret")
	page_id = config.get("fb_credential", "page_id")
	fb_access_token = config.get("fb_credential", "fb_access_token")
	## load jarvis core
	model_directory = 'nlu_model/jarvis_nlu/default/current'
	agent = Agent.load('nlu_dialogue/models/jarvis_nlu', interpreter=RasaNLUInterpreter(model_directory))
	app.run(port=9988)
	
