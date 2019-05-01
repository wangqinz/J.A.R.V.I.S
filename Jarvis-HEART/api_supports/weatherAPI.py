import io, time, json
import requests
from bs4 import BeautifulSoup
## response template
template={}
template['TROUBLE_CONNECT'] = "sorry, I have trouble connecting to the Internet. :("
template['SERVICE_ERROR'] = "sorry, I have trouble getting weather information :("

def query_location(location):
	base = 'http://maps.googleapis.com/maps/api/geocode/json?address='
	try:
		res= requests.get(base+location.replace(" ","+")).json()
	except:
		return None,template['TROUBLE_CONNECT']

	while res['status'] != 'OK':
		time.sleep(3)
		try:
			res= requests.get(base+location.replace(" ","+")).json()
		except:
			return None,template['TROUBLE_CONNECT']

	lat = res['results'][0]['geometry']['location']['lat']
	lng = res['results'][0]['geometry']['location']['lng']
	location = str(lat)+","+str(lng)
	return location, None

def query_weather_today(location):
	## get log/lat of the location
	city = location
	location,err = query_location(location)
	if err:
		return err,None
	## get weather report
	q_type = "today"
	base_weather = 'https://weather.com/weather/'+q_type+'/l/'+location
	try:
		res= requests.get(base_weather)
	except:
		return template['TROUBLE_CONNECT'],None
	## parse information for "today" q_type
	root = BeautifulSoup(res.content, 'html.parser')
	obj = {}
	obj['location'] = city
	try:
		current_weather = root.find("div",class_="today_nowcard-section today_nowcard-condition")
		obj['current_temp_f'] = current_weather.find("div",class_="today_nowcard-temp").find("span").text.strip()
		obj['current_phrase'] = current_weather.find("div",class_="today_nowcard-phrase").text.strip()
		obj['current_feels'] = current_weather.find("div",class_="today_nowcard-feels").find("span",class_="deg-feels").text.strip()
		current_hilo = current_weather.find_all("span",class_="deg-hilo-nowcard")
		obj['current_UV'] = current_weather.find("div",class_="today_nowcard-hilo").find_all("span")[-1].text.strip()
		obj['today_hi'] = current_hilo[0].find("span").text.strip()
		obj['today_lo'] = current_hilo[1].find("span").text.strip()
		obj['preciption_pos'] = root.find("span",class_="precip-val").text.strip()
		obj['today_humidity'] = root.find_all("li",class_="wx-detail")[1].find("span",class_="wx-detail-value").text.strip()
		# obj['today-wind'] = root.find_all("li",class_="wx-detail")[0].find("span",class_="wx-detail-value").text.strip()
		obj['today_wind'] = root.find("span",class_="wx-detail-value wx-wind").text.strip()
	except:
		return template['SERVICE_ERROR'],None

	res = '''
Sure ! It's %(current_phrase)s today in %(location)s :) We have %(preciption_pos)s of chance to get a rainfall.
Right now, the temperature is %(current_temp_f)sF, feels like %(current_feels)sF. 
Today, expect lowest of %(today_lo)sF and highest of %(today_hi)sF. 
The humidity today is %(today_humidity)s, the wind today is %(today_wind)s.
Wish you a good day :-p
	''' % obj
	# print(res)
	return None,res


def query_weather_tmr(location):
	## get log/lat of the location
	city = location
	location,err = query_location(location)
	if err:
		return err,None
	## get weather report
	q_type = "5day"
	base_weather = 'https://weather.com/weather/'+q_type+'/l/'+location
	try:
		res= requests.get(base_weather)
	except:
		return template['TROUBLE_CONNECT'],None
	## parse information for "today" q_type
	root = BeautifulSoup(res.content, 'html.parser')
	obj = {}
	obj['location'] = city
	try:
		root = BeautifulSoup(res.content, 'html.parser')
		trows = root.find("table",class_="twc-table").find_all("tr",class_="clickable")[1]
		temps = trows.find("td", class_="temp").find_all("span",class_="")
		obj['tmr_hi'] = temps[0].text
		obj['tmr_lo'] = temps[1].text
		obj['tmr_phrase'] = trows.find("td", class_="description").find("span").text
		obj['tmr_precip'] = trows.find("td", class_="precip").find_all("span",class_="")[1].text
		obj['tmr_humid'] = trows.find("td", class_="humidity").find_all("span",class_="")[1].text
		obj['tmr_wind'] = trows.find("td", class_="wind").find("span",class_="").text
	except:
		return template['SERVICE_ERROR'],None

	res = '''
Sure! it's %(tmr_phrase)s tomorrow in %(location)s :) We will have %(tmr_precip)s of chance to get a rainfall.
Tomorrow, we will expect lowest of %(tmr_lo)sF and highest of %(tmr_hi)sF. 
The humidity will be %(tmr_humid)s, the wind will be %(tmr_wind)s.
Cheers :-P
	''' % obj
	return None,res

