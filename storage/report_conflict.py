from sqlalchemy import Column, Integer, String, DateTime
from base import Base

import datetime


class ReportConflict(Base):

    __tablename__ = "reported_conflicts"

    id = Column(Integer, primary_key=True)
    node_id = Column(String(250), nullable=False)
    blu_numbers = Column(Integer, nullable=False)
    op_numbers = Column(Integer, nullable=False)
    op_numbers = Column(Integer, nullable=False)
    planet_id = Column(String(100), nullable=False)
    system_id = Column(String(100), nullable=False)
    timestamp = Column(String(100),nullable=False)
    date_created = Column(DateTime, nullable=False)
    trace_id = Column(Integer, nullable=False)

    def __init__(self, node_id, blu_numbers, op_numbers, planet_id, system_id, timestamp, trace_id):
        self.node_id = node_id
        self.blu_numbers = blu_numbers
        self.op_numbers = op_numbers
        self.planet_id = planet_id
        self.system_id = system_id
        self.timestamp = timestamp
        self.date_created = datetime.datetime.now()
        self.trace_id = trace_id

    def to_dict(self):
        dict = {}
        dict['id'] = self.id
        dict['node_id'] = self.node_id
        dict['blu_numbers'] = self.blu_numbers
        dict['op_numbers'] = self.op_numbers
        dict['planet_id'] = self.planet_id
        dict['system_id'] = self.system_id
        dict['timestamp'] = self.timestamp
        dict['date_created'] = self.date_created
        dict['trace_id'] = self.trace_id

        return dict
        