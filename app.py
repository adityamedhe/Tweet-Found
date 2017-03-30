# library dependencies 
from flask import Flask, jsonify, request, make_response
from imgurpython import ImgurClient
from werkzeug.utils import secure_filename
from bson import json_util
from TwitterAPI import TwitterAPI
from datetime import datetime
import time

import os
import json

# my modules
from models.Case import *

# configuring Twitter API
api = TwitterAPI("mwNDCa39VSwGKvmldUz5wufaF",
                 "4nH73L1VCuTrV8ByCiNNVTCrSoo9QAf79L6AYDo8pfhf9HK8tR",
                 "227958848-UxJ7vhdl1DJW1LOq6c1BIrayxBdu2AwtvEar5x1B",
                 "OAXnOgVux5VpRlq58C1SIglDr9QLdlz9gfYVOqDC4f1b4")

app = Flask(__name__)

@app.route("/case", methods=["POST"])
def putCase():
    """ 
        This route creates a new 'case' and enters the same in database.
        Parameters (form-data):
            author
            details
            lat
            lng
            image (file)
        Returns:
            HTTP 200, image_link, id of new case if OK
            HTTP 400 if missing field / data error
            HTTP 500 if any server internal exception / image upload error to Imgur
    """
    try:
        # get all the mandatory fields
        case = Case(author=request.form.get("author", None), case_is_open=True, object_lost=request.form.get("object_lost", None), details=request.form.get("details", None))
        case.location = Location(lat=request.form.get("lat", None), lng=request.form.get("lng", None))
        case.tweets = []
        
        new_id = str(case.save().pk)
        
        # check if file upload present. If yes, POST
        # the same to Imgur via API
        if "image" in request.files:
            file = request.files["image"]
            path = os.path.join(os.getcwd(), "uploads/", file.filename)
            file.save(path)
            
            client = ImgurClient("f0d09803da5a191", "6be459994de860dfcaac69268b00078fdf82f382")
            image = client.upload_from_path(path, config=None, anon=True)
            
            if image is None:
                raise ValidationError("Error in image upload to Imgur")
            
            case.image = image['link']
            case.save()
    except (TypeError, ValidationError) as e:
        return make_response(jsonify({'status': 400, 'message': e.message}), 400)
    except Exception as e:
        print("Exception:", e)
        return make_response(jsonify({'status': 500}), 500)
    else:
        return make_response(jsonify({'status': 200,  'new_id': new_id, 'image_link': case.image}), 200)

@app.route("/case/<id>/", methods=["GET"])
def getCase(id):
    """
        This route returns the document of the case with given id 
        Parameters (route):
            id
        Returns:
            HTTP 200, and document of case if OK
            HTTP 400 if missing field / data error
            HTTP 404 if document not found
            HTTP 500 if any server internal exception
    """
    
    try:
        case = Case.objects(pk=id).as_pymongo()
        if len(case) == 0:
            return make_response(jsonify({'status': 404}), 404)
    except (TypeError, ValidationError) as e:
        return make_response(jsonify({'status': 400}), 400)
    except Exception as e:
        return make_response(jsonify({'status': 500}), 500)
    else:
        return make_response(json_util.dumps({'status': 200, 'case': case[0]}))

@app.route("/case/<id>/close", methods=["POST"])
def closeCase(id):
    """
        This route closes the case with given id 
        Parameters (route):
            id
        Returns:
            HTTP 200, and document of case if OK
            HTTP 400 if missing field / data error
            HTTP 404 if document not found
            HTTP 500 if any server internal exception
    """
    
    try:
        case = Case.objects(pk=id)
        if len(case) == 0:
            return make_response(jsonify({'status': 404}), 404)
        case = case[0]
        case.case_is_open = False
        case.save()
    except (TypeError, ValidationError) as e:
        return make_response(jsonify({'status': 400}), 400)
    except Exception as e:
        print(e)
        return make_response(jsonify({'status': 500}), 500)
    else:
        return make_response(json_util.dumps({'status': 200}))
        
@app.route("/case/<id>/tweet", methods=["POST"])
def tweet(id):
    """
        This route tweets the users in the vicinity of the 
        document's location, if not tweeted in the last 2 hours
        
        Parameters (route):
            id
        Returns:
            HTTP 200, and document of case if OK
            HTTP 400 if missing field / data error
            HTTP 403, if tweeted within last 2 hours
            HTTP 404 if document not found
            HTTP 500 if any server internal exception
    """
    try:
        case = Case.objects(pk=id)
        if len(case) == 0:
            return make_response(jsonify({'status': 404}), 404)
        case = case[0]
        
        # if there are any tweets in this case so far
        if len(case['tweets']) != 0:
            delta = datetime.fromtimestamp(float(time.time())) - datetime.fromtimestamp(float(case['tweets'][len(case['tweets']) - 1]['timestamp']))
        
        # if there are no tweets, or the last tweet was less than 2 hours ago
        if len(case['tweets']) == 0 or (delta is not None and delta.seconds > 10):
            
            # form the geocode string for twitter location query
            geocode_string = str(case['location']['lat']) + "," + str(case['location']['lng']) + ",1km"
            
            # get the tweets from the case's location
            r = api.request('search/tweets', {'q':'', 'geocode': geocode_string})
            
            # if no tweets, tell user 
            if(len(r.json()['statuses']) == 0):
                return make_response(json_util.dumps({'status': 404, 'code':'NO_USERS'}), 404)
                
            # form the new tweets. this function returns an array of tweets with
            # enough tweets required to mention all of the users in the vicinity
            tweets_to_post = form_tweet([i['user']['screen_name'] for i in r.get_iterator()], "Help! site/{}. A missing incident has been reported in your area. Can you help?".format(case.pk))

            # post each tweet, also add to case record
            # for tweet in tweets_to_post:
                # r = api.request('statuses/update', {'status': tweet})
                # case['tweets'].append(Tweet(tweet_id=r.json()['id_str'], timestamp=str(time.time())))
                
            # save the case and respond OK
            case.save()
            return make_response(json_util.dumps({'status': 200}), 200)
        else:
            # last tweet was less than 2 hrs ago, reject
            return make_response(json_util.dumps({'status': 403}), 403)
    except (TypeError, ValidationError) as e:
        return make_response(jsonify({'status': 400}), 400)
    except Exception as e:
        return make_response(jsonify({'status': 500}), 500)

def form_tweet(users, message):
    user_set = set()
    tweets = []
    
    # add the users to a set, to maintain unique users only
    for u in users:
        user_set.add(u)
        
    # begin with a tweet with only an initial message
    tweet = "" + message + " "
    
    # available_length = max tweet length - initial message length
    available_length = 140 - len(message) - 5
    
    # while every user is not added to the tweets
    while len(user_set) > 0:
        # remove a user from the set
        u = user_set.pop()
        if available_length >= len(u):
            # if there is enough space available in tweet, add the user
            tweet += "@" + u + " "

            # adjust the available length
            available_length -= (len(u) + 1)
        else:
            # else if tweet full, add the removed user back
            user_set.add(u)
            
            # add the tweets to final result
            tweets.append(tweet)
            
            # prepare new tweet with only initial message
            tweet = "" + message + " "
            available_length = 140 - len(message) - 5
    
    # if only tweet formed, which is less than max length, add that one
    if len(tweets) == 0:
        tweets.append(tweet)
    
    return tweets
    
app.run(port=8080, host="0.0.0.0", debug=True)