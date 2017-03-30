from mongoengine import *

connect ("tweet_found_db", host="mongodb://ds143990.mlab.com", port=43990, username="adityamedhe", password="n1kh1l")

# ORM: MongoEngine
# We gonna be modeling all the info in a single collection: Case
# Following is the structure for each document:

# {
# 	_id: 111,
# 	Author: "John",
# 	Location: {
#         x: x,
#         y: y
#     },
# 	Details: "String of details",
# 	Tweets: [
#  		{
# 			Tweet_id: 123,
# 			Timestamp: ISO string
# 		},
# 		…
# 	]
# }

class Location(EmbeddedDocument):
    lat = DecimalField(precision=3, rounding='ROUND_HALF_UP', required=True)
    lng = DecimalField(precision=3, rounding='ROUND_HALF_UP', required=True)

class Tweet(EmbeddedDocument):
    tweet_id = StringField(required=True)
    timestamp = StringField(required=True)
    
class Case(Document):
    author = StringField(required=True)
    object_lost = StringField(required=True, max_length=15)
    case_is_open = BooleanField(required=True)
    details = StringField(required=True)
    image = StringField(required=False)
    location = EmbeddedDocumentField(Location)
    tweets = ListField(EmbeddedDocumentField(Tweet))