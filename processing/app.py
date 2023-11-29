import connexion
import yaml
import logging
import logging.config
import datetime
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import json
import os.path
from flask_cors import CORS, cross_origin

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"
with open(app_conf_file, 'r') as f:
   app_config = yaml.safe_load(f.read())

with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App COnf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)
    
if os.path.isfile(app_config['datastore']['filename']):
        f = open(app_config['datastore']['filename'])
        f_content = f.read()
        json_object = json.loads(f_content)
        f.close()
else:
    json_object = {'num_conflicts': 0,
                    'max_blu': 0,
                    'max_op': 0,
                    'num_operations': 0,
                    'max_blu_ships': 0,
                    'max_op_ships': 0,
                    'last_updated': "2023-10-12T11:06:15.894272"}
    file_path = app_config['datastore']['filename']
    with open(file_path, 'w') as data_json:
        json.dump(json_object, data_json, indent=4)
def get_stats():
    if os.path.isfile(app_config['datastore']['filename']):
        f = open(app_config['datastore']['filename'])
        f_content = f.read()
        json_object = json.loads(f_content)
        f.close()
        return json_object, 201
    else:
        logger.error("File does not exist")
        return "stats do not exist", 404

def populate_stats():
    if os.path.isfile(app_config['datastore']['filename']):
        f = open(app_config['datastore']['filename'])
        f_content = f.read()
        json_object = json.loads(f_content)
        f.close()
    else:
        json_object = {'num_conflicts': 0,
                        'max_blu': 0,
                        'max_op': 0,
                        'num_operations': 0,
                        'max_blu_ships': 0,
                        'max_op_ships': 0,
                        'last_updated': "2023-10-12T11:06:15.894272"}
        
    now = datetime.datetime.now()
    timestamp = now.strftime('%Y-%m-%dT%H:%M:%S.%f')
        
    logger.info("start periodic processing")
    response_conflicts = requests.get(f"{app_config['eventstore']['url']}/conflict/new_conflict", params={'timestamp':json_object['last_updated'], 'end_timestamp':timestamp})
    response_operations = requests.get(f"{app_config['eventstore']['url']}/conflict/operation_plan", params = {'timestamp': json_object['last_updated'], 'end_timestamp': timestamp})
    logger.info(f"There have been {len(response_conflicts.json())} conflict logs and {len(response_operations.json())} operations logged since {json_object['last_updated']}")
    if response_operations.status_code != 200:
        logger.error(f"Error from operations received: {response_operations.status_code}")
    elif response_conflicts.status_code != 200:
        logger.error(f"Error from conflicts recieved: {response_conflicts.status_code}")
    
    data_conflicts = response_conflicts.json()
    data_operations = response_operations.json()

    if len(data_conflicts):
        max_blu = max(
            [
                json_object['max_blu'],
                max([float(i["blu_numbers"]) for i in data_conflicts])
            ]
        )
        max_op = max(
            [
                json_object['max_op'],
                max([float(i['op_numbers']) for i in data_conflicts])
            ]
        )
    else: 
        max_blu = json_object['max_blu']
        max_op = json_object['max_op']
    if len(data_operations):
        max_blu_ships = max(
            [
                json_object['max_blu_ships'],
                max([float(i['blu_ships']) for i in data_operations])
            ]
        )
        max_op_ships = max(
            [
                json_object['max_op_ships'],
                max([float(i['op_ships']) for i in data_operations])
            ]
        )
    else:
        max_blu_ships = json_object['max_blu_ships']
        max_op_ships = json_object['max_op_ships']

    
    data_dict = {
        'num_conflicts': json_object['num_conflicts']+len(data_conflicts),
        'max_blu': max_blu,
        'max_op': max_op,
        'num_operations': json_object['num_operations']+len(data_operations),
        'max_blu_ships': max_blu_ships,
        'max_op_ships': max_op_ships,
        'last_updated': timestamp
    }

    f = open(app_config['datastore']['filename'], 'w')
    f.write(json.dumps(data_dict))
    f.close()
    logger.debug(f"The current data is {data_dict}")
    logger.info(f"Processing period ended")


    
def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats,
                  'interval',
                  seconds=app_config['scheduler']['period_sec'])
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml",
            strict_validation = True,
            validate_responses=True)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, debug = True, use_reloader=False)