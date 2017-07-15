import logging
import os

from flask import Flask
from flask_ask import Ask, request, session, question, statement
from lxml import html
import requests, bs4

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)

stations = {'Adams & Wabash': '40680', 'Addison': '41440', 'Armitage': '40660', 'Belmont': '41320', 'Chicago': '40710', 'Clark & Lake': '40380', 'Damen': '40090', 'Diversey': '40530', 'Francisco': '40870', 'Fullerton': '41220', 'Harold Washington Library-State & Van Buren': '40850', 'Irving Park': '41460', 'Kedzie': '41180', 'Kimball': '41290', 'LaSalle & Van Buren': '40160', 'Merchandise Mart': '40460', 'Montrose': '41500', 'Paulina': '41310', 'Quincy': '40040', 'Randolph & Wabash': '40200', 'Rockwell': '41010', 'Sedgwick': '40800', 'Southport': '40360', 'State & Lake': '40260', 'Washington & Wells': '40730', 'Wellington': '41210', 'Western': '41480'}

# Converts the xpath element to a string
def elementToString(element):
    return ''.join(list(element)).strip()

def buildResponseString(asOfTime, stationName):
    return "As of {}, there are no delays at {}".format(asOfTime, stationName)

def getClosestTrain():
    page_request = requests.get('http://www.transitchicago.com/traintracker/arrivaltimes.aspx?sid=40850')


    page = bs4.BeautifulSoup(page_request.text)

    print("Gettig time element")
    time_element = page.select('#ctl06_upTempTime > div > strong')

    asOfTime = time_element[0].getText().strip()
    asOfTime = asOfTime.replace('p', " PM")

    #asOfTime = list(tree.xpath('//*[@id="ctl06_upTempTime"]/div[1]/strong/text()'))

    # Get the element for the station name
    stationName = page.select('.ttar_stationname')[0].getText().strip()

    stationName = stationName.replace('/', " & ")

    return buildResponseString(asOfTime, stationName)


@ask.launch
def launch():
    speech_text = getClosestTrain()
    return question(speech_text).simple_card('Chicago Transit', speech_text)


@ask.intent('StationIntent')
def hello_world():
    speech_text = getClosestTrain()
    return statement(speech_text).simple_card('Chicago Transit', speech_text)


@ask.session_ended
def session_ended():
    return "{}", 200


if __name__ == '__main__':
    if 'ASK_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            app.config['ASK_VERIFY_REQUESTS'] = False
    app.run(debug=True)