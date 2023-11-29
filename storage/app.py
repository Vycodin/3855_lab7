import connexion
from connexion import NoContent
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from report_conflict import ReportConflict
from upload_operation import UploadOperation
import yaml
import logging
import logging.config
import datetime
import json
from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread
from sqlalchemy import and_
import time
import os
if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"
with open('app_conf.yml', 'r') as f:
   app_config = yaml.safe_load(f.read())

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App COnf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)


DB_ENGINE = create_engine(f"mysql+pymysql://{app_config['datastore']['user']}:{app_config['datastore']['password']}@{app_config['datastore']['hostname']}:{app_config['datastore']['port']}/{app_config['datastore']['db']}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

max_retries = app_config["kafka"]["max_retries"]
current_retry = 0
while current_retry < max_retries:
    try:
        logger.info(f'Attempting to connect to Kafka. Retry count: {current_retry}')
        hostname = f"{app_config['events']['hostname']}:{app_config['events']['port']}"
        client = KafkaClient(hosts=hostname)
        topic = client.topics[str.encode(app_config["events"]["topic"])]
        break
    except Exception as e:
        logger.error(f'Connection to Kafka failed. Error:{str(e)}')
        sleep_time = app_config['kafka']['sleep_time']
        time.sleep(sleep_time)
        current_retry +=1
else:
    logger.error("Max Retries reached. Could not connect to Kafka")


def get_conflict_report(timestamp, end_timestamp):
    session = DB_SESSION()

    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S.%f")

    readings = session.query(ReportConflict).filter(and_(ReportConflict.date_created >= timestamp_datetime, ReportConflict.date_created < end_timestamp_datetime))

    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())
    
    session.close()
    
    logger.info("Query for conflict reports after %s returns %d results" % (timestamp, len(results_list)))

    return results_list, 200

def get_operation_plan(timestamp, end_timestamp):
    session = DB_SESSION()

    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f")
    end_timestamp_datetime = datetime.datetime.strptime(end_timestamp, "%Y-%m-%dT%H:%M:%S.%f")

    readings = session.query(UploadOperation).filter(and_(UploadOperation.date_created >= timestamp_datetime, UploadOperation.date_created < end_timestamp_datetime))

    results_list = []

    for reading in readings:
        results_list.append(reading.to_dict())
    
    session.close()
    
    logger.info("Query for operation plans after %s returns %d results" % (timestamp, len(results_list)))

    return results_list, 200

def process_messages():
    """Process event messages"""
    logger.info("Starting Processing")
    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                         reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST)
    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        logger.info("Message: %s" % msg)
        
        payload = msg['payload']

        if msg["type"] == "report_conflict":
            session = DB_SESSION()
            rc = ReportConflict(payload['node_id'], 
                                payload['blu_numbers'], 
                                payload['op_numbers'], 
                                payload['planet_id'], 
                                payload['system_id'], 
                                payload['timestamp'],
                                payload['trace_id'])


            session.add(rc)
            session.commit()
            session.close()
            logger.debug(f'Received event <report_conflict> with a trace id of {payload["trace_id"]}')
            logger.info(f'Connecting to the DB, Hostname: {app_config["datastore"]["hostname"]}, Port: {app_config["datastore"]["port"]}')
        elif msg["type"] == "upload_operation":
            session = DB_SESSION()
            uo = UploadOperation(payload['operation_id'],
                                payload['planet_id'],
                                payload['system_id'],
                                payload['op_type'],
                                payload['timestamp'],
                                payload['blu_ships'],
                                payload['op_ships'],
                                payload['trace_id'])

            session.add(uo)
            session.commit()
            session.close()
            logger.debug(f'Received event <upload_operation> with a trace id of {payload["trace_id"]}')
        consumer.commit_offsets()

app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yaml",
            strict_validation=True,
            validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages, daemon=True)
    t1.start()
    app.run(port=8090)