## story-basic
* greet
- utter_greet
* goodbye
- utter_goodbye

## story identify
* identify
	- utter_identify


## story-weather
* greet
- utter_greet
* request_weather{"location": "pittsburgh"}
- action_req_weather
* thankyou
 - utter_goodbye
 - action_restart

## story-weather1
* request_weather{"location": "pittsburgh"}
- action_req_weather
- action_restart

## story-weather2
* greet
- utter_greet
* request_weather{"location": "pittsburgh"}
- action_req_weather
- action_restart

## story-weather3
* request_weather{"location": "pittsburgh"}
- action_req_weather
* thankyou
 - utter_goodbye
- action_restart

## story-weather4
* request_weather{"location": "pittsburgh"}
- action_req_weather
- action_restart

## story-time
* greet
- utter_greet
* request_time
- action_req_time
* thankyou
- utter_goodbye
- action_restart

## story-time2
* greet
- utter_greet
* request_time
- action_req_time
- action_restart

## story-time3
* request_time
- action_req_time
* thankyou
- utter_goodbye
- action_restart

## story-time4
* request_time
- action_req_time
- action_restart


## thank-1
* thankyou
- utter_thank

## emotion-pos
* emotion_pos
- utter_emo_pos

## emotion-neg
* emotion_neg
-utter_emo_neg


## ask_tmr_weather
* request_weather{"location": "pittsburgh","time": "tomorrow"}
- action_req_weather
- action_restart

## ask_streamer
* request_streamer{"game": "overwatch"}
- action_req_streamer
- action_restart

## set_reminder
* set_reminder{"time":"8:00","content":"write report"}
- action_set_reminder
- action_restart



