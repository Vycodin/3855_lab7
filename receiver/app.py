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

ENDPOINT = 'http://localhost:8090'

with open('app_conf.yml', 'r') as f:
   app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

def report_conflict(body):
    headers = {'content-type': "application/json"}
    trace_id = random.randint(1000, 1000000000)
    body['trace_id'] = trace_id
    logger.info(f'Received event <report_conflict> with a trace id of {trace_id}')
    client = KafkaClient(hosts=f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}')
    topic = client.topics[str.encode(app_config['events']['topic'])]
    producer = topic.get_sync_producer()
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

def upload_operation(body):
    headers = {'content-type': "application/json"}
    trace_id = random.randint(1000, 1000000000)
    body['trace_id'] = trace_id
    logger.info(f'Received event <upload_operation> with a trace id of {trace_id}')
    client = KafkaClient(hosts=f'{app_config["events"]["hostname"]}:{app_config["events"]["port"]}')
    topic = client.topics[str.encode(app_config['events']['topic'])]
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