from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from rasa_core.channels import HttpInputChannel
from rasa_core.channels.facebook import FacebookInput
from rasa_core.agent import Agent
from rasa_core.interpreter import RegexInterpreter

import argparse
import logging
import warnings
import time,json
from datetime import *
from pytz import timezone

from policy import RestaurantPolicy
from rasa_core import utils
from rasa_core.actions import Action
from rasa_core.actions.forms import *
from rasa_core.agent import Agent
from rasa_core.channels.console import ConsoleInputChannel
from rasa_core.events import SlotSet
from rasa_core.featurizers import (
	MaxHistoryTrackerFeaturizer,
	BinarySingleStateFeaturizer)
from rasa_core.interpreter import RasaNLUInterpreter
from rasa_core.policies.memoization import MemoizationPolicy
from rasa_core.policies.fallback import FallbackPolicy
from rasa_core.events import AllSlotsReset
from rasa_core.events import Restarted
#### api loading
import sys
sys.path.insert(0, 'api_supports/')
from weatherAPI import *
from twitchAPI import *
from reminderAPI import *

######################################################
'''         return message templates       
	- format:   <api> D  <function> D  <err> D<params>
	- delimit = "$$"
'''
######################################################


######################################################
'''         action class and functions functions       '''
######################################################
# class setReminder(FormAction):
#     RANDOMIZE = False
#     @staticmethod
#     def required_fields():
#         return [
#             EntityFormField("time", "time"),
#             EntityFormField("content", "content"),
#         ]

#     def name(self):
#         return "action_set_reminder"

#     def submit(self, dispatcher, tracker, domain):
#         time = tracker.get_slot("time")
#         content = tracker.get_slot("content")
#         print(time, content)
#         reply = setReminderWithFull({'time':time,'content':content})
#         dispatcher.utter_message(reply)
#         return[]

######################################################
'''         user info related class       '''
######################################################
class setReminder(Action):
	def name(self):
		return "action_set_reminder"
	def run(self, dispatcher, tracker, domain):
		time = tracker.get_slot("time")
		content = tracker.get_slot("content")
		time = time if time else 'None'
		content = content if content else 'None'
		req = {'action':'action_set_reminder','err':None,'function':"setReminder",
		'param':'time##'+time+",content##"+content}
		dispatcher.utter_message("apiCall$%$"+json.dumps(req))
		return

class AskWeather(Action):
	def name(self):
		return "action_req_weather"
	def run(self, dispatcher, tracker, domain):
		# dispatcher.utter_message("searching weather")
		location = tracker.get_slot("location")
		time = tracker.get_slot("time")
		if location == None:
			location = 'None'
		if time == None:
			time = 'None'
		
		# print(time)
		req = {"action":"action_req_weather",'err':None,'function':"handle_weather_req",
		'param':"location:"+location+",time:"+time}


		dispatcher.utter_message("apiCall$%$"+json.dumps(req))
		return

class AskTime(Action):
	'''
	action for searching time 
	'''
	def name(self):
		return "action_req_time"
	def run(self, dispatcher, tracker, domain):
		req = {'action':"action_req_time",'err':None,'function':"askTime"}
		## api call
		dispatcher.utter_message("apiCall$%$"+json.dumps(req))
		return   

######################################################
'''         general classes       '''
######################################################

class checkTwich(Action):
	def name(self):
		return "action_req_streamer"
	def run(self, dispatcher, tracker, domain):
		game = tracker.get_slot("game")
		# print(game)
		if game == None:
			reply = "sry, I need a category"
		else:
			qset = {'game':game,'limit':10}
			reply = query_game_streamers(qset)
		dispatcher.utter_message(reply)
		return

######################################################
'''         basic train/run functions       '''
######################################################

def train_dialogue(domain_file="../rasa/jarvis_dom.yml",
				   model_path="nlu_dialogue/models/jarvis_nlu",
				   training_data_file="../rasa/jarvis_story.md"):
	fallback = FallbackPolicy(fallback_action_name="utter_default", core_threshold = 0.46, nlu_threshold = 0.46)
	agent = Agent(domain_file,
				  policies=[MemoizationPolicy(max_history=3),
							RestaurantPolicy(), fallback])

	training_data = agent.load_data(training_data_file)
	agent.train(
			training_data,
			epochs=400,
			batch_size=100,
			validation_split=0.2
	)

	agent.persist(model_path)
	return agent


def train_nlu(): # pipline
	from rasa_nlu.training_data import load_data
	from rasa_nlu import config
	from rasa_nlu.model import Trainer

	# training_data = load_data('../rasa/data/res_data.json')
	training_data = load_data('./data_loading/test_loading.json')
	trainer = Trainer(config.load("../rasa/config.yml"))
	trainer.train(training_data)
	model_directory = trainer.persist("./nlu_model/jarvis_nlu/",fixed_model_name="current")

	return model_directory


def run(serve_forever=True):
	# interpreter = RasaNLUInterpreter("models/nlu/default/current")
	# agent = Agent.load("models/dialogue", interpreter=interpreter)
	interpreter = RasaNLUInterpreter("nlu_model/jarvis_nlu/default/current")
	agent = Agent.load("nlu_dialogue/models/jarvis_nlu", interpreter=interpreter)
   
	if serve_forever:
		agent.handle_channel(ConsoleInputChannel())
	return agent


def run_cloud(serve_forever=True):
	fb_verify = "jarvis_demo_v1"
	fb_secret = "16de4c12bff8562acdf093063115cf5f"
	page_id = "253402548804134"
	fb_access_token = "EAADmdZBDoGiYBADkbun1mP1I3NmWevWW0Mtj5BItxGM2akMdIrqqIGgUIIRvgJMmVQojpRqfZBgWXcpdZBlL6N3woLnISCRD0AuLT76gIbKFZB7HJYdaNxzsyus8MVjlyngTqRonDSdUrcoMYXlflXvSlHvzSsNkXXZB5s9iY5wZDZD"

	input_channel = FacebookInput(
	   fb_verify=fb_verify,  # you need tell facebook this token, to confirm your URL
	   fb_secret=fb_secret,  # your app secret
	   fb_access_token=fb_access_token,   # token for the page you subscribed to
	)

	interpreter = RasaNLUInterpreter("nlu_model/jarvis_nlu/default/current")
	agent = Agent.load("nlu_dialogue/models/jarvis_nlu", interpreter=interpreter)
   
	if serve_forever:
		agent.handle_channel(HttpInputChannel(9988, "", input_channel))
	return agent




if __name__ == '__main__':
	utils.configure_colored_logging(loglevel="INFO")

	parser = argparse.ArgumentParser(
			description='starts the bot')

	parser.add_argument(
			'task',
			choices=["train-nlu", "train-dialogue", "run-l","run-c"],
			help="what the bot should do - e.g. run or train?")
	task = parser.parse_args().task

	# decide what to do based on first parameter of the script
	if task == "train-nlu":
		train_nlu()
	elif task == "train-dialogue":
		train_dialogue()
	elif task == "run-l":
		run()
	elif task == "run-c":
		run_cloud()


######################################################
'''         backup functions       '''
######################################################

class RestaurantAPI(object):
	def search(self, info):
		print(info)
		return "papi's pizza place"


class ActionSearchRestaurants(Action):
	def name(self):
		return 'action_search_restaurants'

	def run(self, dispatcher, tracker, domain):
		dispatcher.utter_message("looking for restaurants")
		restaurant_api = RestaurantAPI()
		query = {}
		query['cuisine'] = tracker.get_slot("cuisine")
		query['people'] = tracker.get_slot("people")
		query['location'] = tracker.get_slot("location")
		query['price'] = tracker.get_slot("cuisine")
		query['info'] = tracker.get_slot("cuisine")
		print(query)
		restaurants = restaurant_api.search(query)
			
		return [SlotSet("matches", restaurants)]


class ActionSuggest(Action):
	def name(self):
		return 'action_suggest'

	def run(self, dispatcher, tracker, domain):
		dispatcher.utter_message("here's what I found:")
		dispatcher.utter_message(tracker.get_slot("matches"))
		dispatcher.utter_message("is it ok for you? "
								 "hint: I'm not going to "
								 "find anything else :)")
		return []




