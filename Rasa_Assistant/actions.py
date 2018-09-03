from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_core_sdk import Action
from rasa_core_sdk.events import SlotSet, AllSlotsReset
import requests
import json
from random import randint
import datetime
import os
import yaml




class ActionPlaceSearch(Action):
    def name(self):
        return 'action_place_search'

    def run(self, dispatcher, tracker, domain):
        query = tracker.get_slot('query')
        radius = tracker.get_slot('number')		

        with open("./credentials.yml", 'r') as ymlfile:
            cfg = yaml.load(ymlfile)
        key = cfg['credentials']['GOOGLE_KEY']
		
		
        get_origin = requests.post(
            "https://www.googleapis.com/geolocation/v1/geolocate?key={}".format(key)).json()
        origin_lat = get_origin['location']['lat']
        origin_lng = get_origin['location']['lng']
				

        place = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={},{}&radius={}&type={}&key={}'.format(origin_lat, origin_lng, radius, query, key)).json()
        if len(place['results'])==0:
            dispatcher.utter_message("Sorry, I didn't find anything")
            return [SlotSet('location_match', 'none')]
        else:
            for i in place['results']:
                if 'rating' and 'vicinity' in i.keys():				
                    name = i['name']
                    rating = i['rating']
                    address = i['vicinity']
                    if i['opening_hours']['open_now']==True:
                        opening_hours = 'open'
                    else:
                        opening_hours = 'closed'
                    break
            speech = "I found a {} called {} based on your specified parameters.".format(query, name)
            dispatcher.utter_message(speech)	
            return [SlotSet('location_match', 'one'), SlotSet('rating', rating), SlotSet('address', address), SlotSet('opening_hours', opening_hours)]


