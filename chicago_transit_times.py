import logging
import os
from flask import Flask
from flask_ask import Ask, request, session, question, statement
from lxml import html
import requests, bs4
from datetime import datetime
app = Flask(__name__)
ask = Ask(app, "/")
#logging.getLogger('flask_ask').setLevel(logging.DEBUG)

route_dict = {"Red": "Red Line", "P": "Purple Line", "Brn":"Brown Line", "Org": "Orange Line", "G":"Green Line", "Blue": "Blue Line", "Y": "Yellow Line", "Pink":"Pink Line"}

# just brown line trains currently
stations = {'Adams Wabash': '40680', 'Addison': '41440', 'Armitage': '40660', 'Belmont': '41320', 'Chicago': '40710', 'Clark & Lake': '40380', 'Damen': '40090', 'Diversey': '40530', 'Francisco': '40870', 'Fullerton': '41220', 'Harold Washington Library-State & Van Buren': '40850', 'Irving Park': '41460', 'Kedzie': '41180', 'Kimball': '41290', 'LaSalle & Van Buren': '40160', 'Merchandise Mart': '40460', 'Montrose': '41500', 'Paulina': '41310', 'Quincy': '40040', 'Randolph & Wabash': '40200', 'Rockwell': '41010', 'Sedgwick': '40800', 'Southport': '40360', 'State & Lake': '40260', 'Washington & Wells': '40730', 'Wellington': '41210', 'Western': '41480'}
KEY = "" #intentionally hidden for git
api_base_url= "http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx?"

time_format = "%Y-%m-%dT%H:%M:%S"

class Arrival:
    def __init__(self, arrival_data):
        self.arrival_time = datetime.strptime(arrival_data['arrT'], time_format)
        self.last_time = datetime.strptime(arrival_data['prdt'], time_format)
        self.route = route_dict[arrival_data['rt']]
        self.station_name = arrival_data['staNm']
    def get_prediction(self):
        return ((self.arrival_time-self.last_time).seconds//60)%60
    def response_string(self):
        return "There is a {} train arriving in {} minutes at {}.".format(self.route,
                                                                               self.get_prediction(),
                                                                               self.station_name)
# unused, but might use to update the list of trains
def get_all_station_info():
    url = "https://data.cityofchicago.org/resource/8mj8-j3c4.json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
    station_dict = dict((d["stop_name"], d["map_id"]) for d in data)

def get_next_arrival(station_request):
    map_id = 0

    # if the name isnt quite right, try to guess it from known names
    if station_request not in stations.keys():
        # Look up the term in the list of stations
        for key in stations.keys():
            if station_request in key:
                map_id = stations[key]
                station_request = key

        if not map_id:
            return "I'm sorry, I couldn't find the station: {}".format(station_request)
    else:
        map_id = stations[station_request]

    # pull data from CTA API
    url = "{}mapid={}&key={}&outputType=JSON".format(api_base_url,map_id,KEY)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()

    # get just the next train, for now
    print(data)
    next_data = data['ctatt']['eta'][0]

    next_arrival = Arrival(next_data)

    return next_arrival.response_string()

@ask.launch
def launch():
    speech_text = "What information are you looking for?"
    return question(speech_text).simple_card('Chicago Transit', speech_text)


@ask.intent('ArrivalIntent')
def arrival_intent(station):
    speech_text = get_next_arrival(station)
    return statement(speech_text).simple_card('Chicago Transit', speech_text)


@ask.session_ended
def session_ended():
    return "{}", 200


if __name__ == '__main__':
    if 'ASK_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            app.config['ASK_VERIFY_REQUESTS'] = False
    app.run(debug=False)