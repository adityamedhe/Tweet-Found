from flask import Flask, jsonify, request, Response
from models.Case import *

app = Flask(__name__)

@app.route("/case/put", methods=["POST"])
def putCase():
    reqJson = request.get_json()
    response = Response(status=406)
    # if reqJson is None:
    return (response)
    

app.run(port=8080, host="0.0.0.0")