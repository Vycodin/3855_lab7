import connexion
from connexion import NoContent
import requests
import yaml
import logging
import logging.config
import random
import json
import  datetime
from pykafka import KafkaClient
import time
import os
ENDPOINT = 'http://localhost:8090'

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
max_retries = app_config["kafka"]["max_retries"]
current_retry = 0
while current_retry < max_retries:
    try:
        logger.info(f'Attempting to create Kafka Client. Retry count: {current_retry}')
        client = KafkaClient(hosts=f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}')
        topic = client.topics[str.encode(app_config['events']['topic'])]
        logger.info(f'Succesful connection')
        producer = topic.get_sync_producer()
        break
    except Exception as e:
        logger.error(f'Kafka creation failed. Error:{str(e)}')
        sleep_time = app_config['kafka']['sleep_time']
        time.sleep(sleep_time)
        current_retry +=1
else:
    logger.error("Max Retries reached. Could not connect to Kafka")

def report_conflict(body):
    trace_id = random.randint(1000, 1000000000)
    body['trace_id'] = trace_id
    logger.info(f'Received event <report_conflict> with a trace id of {trace_id}')
    msg = { "type": "report_conflict",
        "datetime" :
        datetime.datetime.now().strftime(
        "%Y-%m-%dT%H:%M:%S"),
        "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    # response = requests.post(f"{app_config['conflictLog']['url']}", json = body, headers=headers)
    logger.info(f'Returned event <report_conflict> reponse {trace_id} with status 201')
    
    return NoContent, 201
def healthCheck():
    return NoContent, 200
def upload_operation(body):
    trace_id = random.randint(1000, 1000000000)
    body['trace_id'] = trace_id
    logger.info(f'Received event <upload_operation> with a trace id of {trace_id}')
    producer = topic.get_sync_producer()
    msg = { "type": "upload_operation",
        "datetime" :
        datetime.datetime.now().strftime(
        "%Y-%m-%dT%H:%M:%S"),
        "payload": body}
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    #response = requests.post(f"{app_config['operationLog']['url']}", json = body, headers=headers)
    logger.info(f'Returned event <upload_operation> reponse {trace_id} with status 201')
    return NoContent, 201


    



app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",
            strict_validation=True,
            validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080, debug=True)