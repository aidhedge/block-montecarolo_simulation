import os
from flask import Flask
from flask import jsonify
from flask import request
import json
from cerberus import Validator
from exceptions import payLoadIsMissing
from exceptions import malformedJson
from exceptions import payloadNotMatchingSchema
app = Flask(__name__)


@app.errorhandler(payLoadIsMissing)
@app.errorhandler(payloadNotMatchingSchema)
@app.errorhandler(malformedJson)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def hello():
    return "Hello World!"

@app.route("/simulate", methods=['POST'])
def simulate():
    payload_schema = {
                    'pair': {'type': 'string', 'required': True},
                    'from_date': {'type': 'string', 'required': True},
                    'to_date': {'type': 'string', 'required': True}
                    }
    validate = Validator(payload_schema)
    
    payload = request.form.get('payload', None)
    if not(payload):
        raise payLoadIsMissing('There is no payload', status_code=500)
    try:
        payload = json.loads(payload)
    except:
        raise malformedJson("Payload present but malformed")
    if validate(payload):
        return 'OK'
    else:
        raise payloadNotMatchingSchema("Payload didn't match schema ({})".format(str(payload_schema)))
        

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)