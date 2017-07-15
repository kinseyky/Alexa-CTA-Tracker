import logging
import os

from flask import Flask
from flask_ask import Ask, request, session, question, statement
from lxml import html
import requests

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger('flask_ask').setLevel(logging.DEBUG)

# Converts the xpath element to a string
def elementToString(element):
    return ''.join(list(element)).strip()

def buildResponseString(asOfTime, stationName):
    return "As of {}, there are no delays at {}".format(asOfTime, stationName)

def getClosestTrain():
    page = requests.get('http://www.transitchicago.com/traintracker/arrivaltimes.aspx?sid=40850')
    tree = html.fromstring(page.content)

    asOfTime = list(tree.xpath('//*[@id="ctl06_upTempTime"]/div[1]/strong/text()'))

    # Get the element for the station name
    stationName = elementToString(tree.xpath('//div[@class="ttar_stationname"]/text()'))
    stationName = stationName.replace('/', " & ")

    asOfTime = elementToString(tree.xpath('//*[@id="ctl06_upTempTime"]/div[1]/strong/text()'))
    asOfTime = asOfTime.replace('p', " PM")

    return buildResponseString(asOfTime, stationName)


@ask.launch
def launch():
    speech_text = "What would you like to know about the CTA?"
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