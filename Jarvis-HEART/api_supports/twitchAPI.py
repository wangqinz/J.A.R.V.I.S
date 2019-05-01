import io, time, json,os
import requests
from configparser import ConfigParser

config = ConfigParser()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config.read(os.path.join(BASE_DIR, 'auth.ini'))
client_id = config.get("auth", "twitch")
template = {}
template['SERVICE_ERROR'] = "sorry, I have trouble getting information :("


def query_game_streamers(q_set):
	game = q_set['game']
	limit = q_set['limit']
	headers = {"Client-ID":client_id}
	try:
		response = requests.get("https://api.twitch.tv/kraken/search/streams?query="+game, headers=headers).json()
		result = "{:<15} {:<5} {:<10} \n".format("name","viewers","status")
		for ele in response['streams'][:limit]:
			name = ele['channel']['name']
			viewers = ele['viewers']
			status = ele['channel']['status']
			result += "{:<10} {:<10} {:<10} \n".format(name,viewers,status)
		# print(result)
		res_dict = {}
		res_dict['game'] = q_set['game']
		res_dict['data'] = result
		res = '''
	Okay. Here is what I found for %(game)s.\n %(data)s.\nCheers :-p
		'''	%res_dict
		return res
	except:
		return template['SERVICE_ERROR']

ded query_game_end(p_set):
    if q_set["game"]:
    limit =
	


