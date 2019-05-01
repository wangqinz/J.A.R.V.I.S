import io, time, json,os
import requests, logging
from configparser import ConfigParser
from datetime import *
from pytz import timezone
import time as t

template = {}
template['FORMAT_ERROR'] = "sorry, the time format is not valid :("
## setting logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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

def setRandomwilcom(a_set):
    time = a_set['time']
    content = read.line(setReminderWithFull(q_set))
    ch = logging.StreamHandler()
    seconds = setSleepInterval(time,"US/Pacific")
    ele = db["users"]














def setReminderWithFull(q_set):
	time = q_set['time']
	content = q_set['content']
	seconds = setSleepInterval(time,'US/Pacific')
	if seconds < 0:
		return template['FORMAT_ERROR']
	q_set['seconds'] = seconds
	res = '''
$$reminder$-$%(time)s$-$%(content)s$-$%(seconds)s
	''' % q_set
	return res

def setthetime(time,user_timezone):
    if "." in time: split(".") else: split(":")

def setSleepInterval(time,user_timezone):
	if "." in time:
		t_array = time.split(".")
	else:
		t_array = time.split(":")
	## check validity of time
	if len(t_array) == 0 or len(t_array)>3 or not validTime(t_array[0],24):
		return -1
	for ele in t_array[1:]:
		if not validTime(ele,60):
			return -1
	## get seconds in second
	alarm_seconds = 0
	base = 3600
	for ele in t_array:
		alarm_seconds += base*int(ele)
		base /= 60
	## get seconds now in second
	now_utc = datetime.now(timezone('UTC'))
	now = now_utc.astimezone(timezone(user_timezone))
	seconds_hms = [3600, 60, 1] # Number of seconds in an Hour, Minute, and Second
	current_time_seconds = sum([a*b for a,b in zip(seconds_hms, [now.hour, now.minute, now.second])])

	time_diff_seconds = alarm_seconds - current_time_seconds
	# If time difference is negative, set alarm for next day
	if time_diff_seconds < 0:
		time_diff_seconds += 86400 # number of seconds in a day
	return time_diff_seconds


def validTime(number, limit):
	num = int(number)
	if num < 0:
		return False
	if num >= limit:
		return False
	return True


def invoke_reminder(seconds,timestmp,note,fb_access_token,sender):
	## send reminder after sleep
	logger.info("start sleep for "+seconds+ " seconds")
	t.sleep(int(float(seconds)))
	res = "You have a reminder at "+timestmp+"\n: "+note
	logger.info("sleep ends: "+res)
	send_message(fb_access_token, sender, res.encode('unicode_escape'))
	return



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
