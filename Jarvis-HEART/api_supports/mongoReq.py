from pymongo import *
from configparser import ConfigParser
import os,logging

config = ConfigParser()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config.read(os.path.join(BASE_DIR, 'auth.ini'))
mongo_ip = str(config.get("auth", "mongo_ip"))
mongo_port = int(config.get("auth", "mongo_port"))

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

def get_jarvis_db():
	print(mongo_ip,mongo_port)
	client = MongoClient(mongo_ip,mongo_port)
	db = client['jarvis']
	return db

def get_user_collection():
	db = get_jarvis_db()
	return db['users']

def get_user_obj(uid):
	users = get_user_collection()
	return users.find_one({'id':uid})












###################################################
############## bridge helper function ##############

def get_mongo_user_timezone(user_id,dft_timezone):
	user_obj = get_user_obj(user_id)
	if user_obj == None:
		## user does not exist
		tzone = dft_timezone
		logger.warning("mongo access (no rcd)>> %s",{"uid":user_id})
	else:
		tzone = user_obj['timezone']
	return tzone

def get_mongo_user_location(user_id,dft_location):
	user_obj = get_user_obj(user_id)
	if user_obj == None:
		## user does not exist
		location = dft_location
		logger.warning("mongo access (no rcd)>> %s",{"uid":user_id})
	else:
		location = user_obj['location']
	return location

		