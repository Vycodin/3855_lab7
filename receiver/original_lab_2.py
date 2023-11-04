import connexion
from connexion import NoContent
import json
import datetime
import os.path

FILE_NAME = 'data.json'
MAX_EVENTS = 10

def report_conflict(body):
    message = f"A new conflict arises on the {body['planet_id']} within {body['system_id']}. The {body['conflict_details']['blufor']['blufor_id']} fight valiantly against the {body['conflict_details']['opfor']['opfor_id']} to secure the {body['planet_id']} for the God-Emperor! Ave Imperator!"
    log_data(message)
    return NoContent, 201

def upload_operation(body):
    message = f"Attention. {body['operation_id']} plans have been uploaded. This will be a {body['op_type']} on the planet {body['planet_id']}. Ave Imperator!"
    log_data(message)
    return NoContent, 201

def log_data(message):
    current_datetime = datetime.datetime.now()
    current_datetime_str = current_datetime.strftime("%y-%m-%d %H:%M:%S")
    request_data = {
        "recieved_timestamp": current_datetime_str,
        "recieved_data": message
    }
    json_array = []
    if os.path.isfile(FILE_NAME):
        f = open(FILE_NAME, 'r')
        f_content = f.read()
        json_array = json.loads(f_content)
        f.close()

    json_array.insert(0, request_data)
    if len(json_array) > MAX_EVENTS:
        json_array.pop()

    f = open(FILE_NAME, 'w')
    f.write(json.dumps(json_array, indent = 2))
    f.close()
    



app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",
            strict_validation=True,
            validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080, debug=True)