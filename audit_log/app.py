import connexion
from connexion import NoContent
import yaml
import logging
import logging.config
import datetime
import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
from flask_cors import CORS, cross_origin
import os

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
def get_conflict_report(index):
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]['port'])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=1000)
    logger.info("Retrieving Conflict report at index %d" % index)
    conflicts = []
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg['type'] == 'report_conflict':
                conflicts.append(msg)
            for x,msg in enumerate(conflicts):
                if x == index:
                    return msg, 200
    except:
        logger.error("No more messages found")
    logger.error("Could not find report at index %d" % index)
    return {"message":"Not Found"}, 404
def get_operation_report(index):
    hostname = "%s:%d" % (app_config["events"]["hostname"],
                          app_config["events"]['port'])
    client = KafkaClient(hosts=hostname)
    topic = client.topics[str.encode(app_config["events"]["topic"])]

    consumer = topic.get_simple_consumer(reset_offset_on_start=True,
                                         consumer_timeout_ms=1000)
    logger.info("Retrieving Operation report at index %d" % index)
    operations = []
    try:
        for msg in consumer:
            msg_str = msg.value.decode('utf-8')
            msg = json.loads(msg_str)
            if msg['type'] == 'upload_operation':
                operations.append(msg)
            for x,msg in enumerate(operations):
                if x == index:
                    return msg, 200
    except:
        logger.error("No more messages found")
    logger.error("Could not find report at index %d" % index)
    return {"message":"Not Found"}, 404

def healthCheck():
    return 200

app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yaml",
            strict_validation=True,
            validate_responses=True)

if __name__ == "__main__":
    app.run(port=8110)