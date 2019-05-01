from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from django.conf import settings
from django.db import transaction
from django.shortcuts import render, redirect
from datetime import datetime
import os, tempfile, zipfile,tarfile, time

from rasa_nlu.model import Metadata, Interpreter
from rasa_nlu import config
from rasa_nlu.model import Trainer
from rasa_core.agent import Agent
from rasa_core.interpreter import RasaNLUInterpreter

##run durectly
'''
python -m rasa_core.run -d nlu_dialogue/models/restaurant -u nlu_model/restaurant/default/model_20180620-224333
'''

model_directory = 'nlu_model/jarvis_nlu/default/current'
# interpreter = Interpreter.load(model_directory)
agent = Agent.load('nlu_dialogue/models/jarvis_nlu', interpreter=RasaNLUInterpreter(model_directory))
# Create your views here.

def home(requests):
	return render(requests, 'jarvis/home.html',{})

def task(requests):
	req = requests.GET['query']
	context = {}
	
	### using NLU intent prediction
	# intent = interpreter.parse(req)
	# print(intent)
	# context['message'] = intent

	### using rasa core intent prediction
	responses = agent.handle_message(req)
	print(responses)
	context['message'] = responses
	context['input'] = req
	return render(requests, 'jarvis/home.html',context)




