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
# 			Time: ISO string,
# 			Users: [user1, user2, ...]
# 		},
# 		…
# 	]
# }

class Location(EmbeddedDocument):
    lat = DecimalField(precision=3, rounding='ROUND_HALF_UP')
    lng = DecimalField(precision=3, rounding='ROUND_HALF_UP')

class Tweet(EmbeddedDocument):
    tweet_id = StringField(required=True)
    time = StringField(required=True)
    users = ListField(StringField(required=True))
    
class Case(Document):
    author = StringField(required=True)
    details = StringField(required=True)
    location = EmbeddedDocumentField(Location)
    tweets = ListField(EmbeddedDocumentField(Tweet))