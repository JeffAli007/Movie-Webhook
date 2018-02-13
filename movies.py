#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from random import randint

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os
import requests

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)
movieDetails = "Plot"

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") != "movies.details":
        return {}
    baseurl = "http://www.omdbapi.com/?"
    dynamic_Content = getDynamicContent(req)
    if dynamic_Content is None:
        return {}
    final_url = baseurl + urlencode({'apikey':'6a614a70','plot':'full','t': dynamic_Content})
    result = requests.get(final_url)
    data = json.loads(result.text)
    res = makeWebhookResult(data)
    return res


def getDynamicContent(req):
    result = req.get("result")
    parameters = result.get("parameters")
    movie = parameters.get("any")
	
    if (parameters.get("movie_details")) != "":
        global movieDetails
        movieDetails = parameters.get("movie_details")
	
    if movie is None:
        return None
      
    return movie


def makeWebhookResult(data):
    info = data[movieDetails]
    if info is None:
        return {}
    
    movie = data['Title']
	
    speech = movie + " movie's " + movieDetails + " is " + info
    displayText = movie + " movie's " + movieDetails + " is " + info
    
    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": displayText,
        "data": {} ,
        "contextOut": [],
        "source": "apiai-movie-webhook"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=True, port=port, host='0.0.0.0')
