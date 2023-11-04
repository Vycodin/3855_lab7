from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime

class UploadOperation(Base):


    __tablename__ = "upload_operation"

    id = Column(Integer, primary_key=True)
    operation_id = Column(String(250), nullable=False)
    planet_id = Column(String(100), nullable=False)
    system_id = Column(String(100), nullable=False)
    op_type = Column(String(100), nullable=False)
    timestamp = Column(String(100), nullable=False)
    blu_ships = Column(Integer, nullable=False)
    op_ships = Column(Integer, nullable=False)
    date_created = Column(DateTime, nullable=False)
    trace_id = Column(Integer, nullable=False)

    def __init__(self, operation_id, planet_id, system_id, op_type,timestamp, blu_ships, op_ships, trace_id):
        self.operation_id = operation_id
        self.planet_id = planet_id
        self.system_id = system_id
        self.op_type = op_type
        self.timestamp = timestamp
        self.blu_ships = blu_ships
        self.op_ships = op_ships
        self.date_created = datetime.datetime.now()
        self.trace_id = trace_id
    
    def to_dict(self):
        dict = {}
        dict['id'] = self.id
        dict['operation_id'] = self.operation_id
        dict['planet_id'] = self.planet_id
        dict['system_id'] = self.system_id
        dict['timestamp'] = self.timestamp
        dict['op_type'] = self.op_type
        dict['blu_ships'] = self.blu_ships
        dict['op_ships'] = self.op_ships
        dict['date_created'] = self.date_created
        dict['trace_id'] = self.trace_id

        return dict