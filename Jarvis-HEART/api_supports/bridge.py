import sys
import json, os, logging
import requests
from datetime import datetime
from multiprocessing import Process
from configparser import ConfigParser

from weatherAPI import *
from twitchAPI import *
from reminderAPI import *

import requests,time,os,json

from mongoReq import *
######################################################
###########			logger config 		###########
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
##level:  DEBUG, INFO, WARNING, ERROR, CRITICAL
handler = logging.FileHandler('../jarvis_fail.log')
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

######################################################
'''         return message templates       
	- format:   <api> D  <function> D  <err> D<params>
	- delimit = "$$"
'''
######################################################
###########		global data		############ 
dft_timezone = 'US/Pacific'
dft_location = "San Francisco"

def setReminder(params):
	err = params['err']
	if err != None:
		return err, err
	p = {ele.split("##")[0]: ele.split("##")[1] for ele in params['param'].split(",")}
	## check missing information
	if p['time'] == 'None':
		err = "sorry, but I need a time (in 24 hour clock) to set up reminder"

	elif p['content'] == 'None':
		err = "lack reminder content"
	else:
		## set reminder
		### need to retrieve user_related time zone info
		tzone = get_mongo_user_timezone(str(params['sender']),dft_timezone)

		seconds = setSleepInterval(p['time'],tzone)
		if seconds < 0:
			err = "sorry, the time format is not valid :("
		else:
			## set reminder, start sleep, return value
			process = Process(target=invoke_reminder, 
				args=(seconds,p['time'],p['content'],params['fb_access_token'],params['sender']))
			process.start()
			reply = "okay :) reminder set at "+p['time']+":\t"+p['content']

	if err:
		return err,err
	else:
		return None,reply

def handle_weather_req(params):
	err = params['err']
	if err != None:
		return err, err
	p = {ele.split(":")[0]: ele.split(":")[1] for ele in params['param'].split(",")}
	## get location info
	if p['location'] == 'None':
		## need to retrieve location from mongo
		user_id = str(params['sender'])
		p['location'] = get_mongo_user_location(user_id, dft_location)

	if p['time'] == 'None':
		err, reply = query_weather_today(p['location'])
	elif p['time'] in ['tomorrow','tmr']:
		err, reply = query_weather_tmr(p['location'])
	else:
		err = "I can only get today and tomorrow's weather :( sorry"

	if err:
		return err,err
	else:
		return None, reply




def askTime(params):
	# time
	# dispatcher.utter_message("searching time")
	err = params['err']
	if err != None:
		return err, err
	# in python 3.5.2, astimezone() cannot be applied to a naive datetime\
	f = "%Y-%m-%d %H:%M:%S"
	f_less = "%H:%M"
	
	## get user tinezone
	user_id = str(params['sender'])
	tzone = get_mongo_user_timezone(user_id,dft_timezone)

	now_utc = datetime.now(timezone('UTC'))
	nowtime = now_utc.astimezone(timezone(tzone))
	# print(dfttime)
	tmptime = nowtime.strftime(f_less)
	return None,"It's "+ tmptime + " now !"





def deliver_tasks(params):

	func = params['function']
	err, reply = globals()[func](params)
	return {'err':err,'msg':reply}



