# database/models.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

Base = declarative_base()

class TaskPlan(Base):
    __tablename__ = 'task_plans'
    
    id = Column(Integer, primary_key=True)
    goal = Column(String(500), nullable=False)
    plan_steps = Column(Text, nullable=False)  # JSON string
    enriched_info = Column(Text)  # JSON string for external data
    status = Column(String(50), default='completed')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def get_plan_steps_list(self):
        """Convert JSON string back to list"""
        try:
            return json.loads(self.plan_steps) if self.plan_steps else []
        except:
            return []
    
    def set_plan_steps_list(self, steps_list):
        """Convert list to JSON string"""
        self.plan_steps = json.dumps(steps_list)
    
    def get_enriched_info_dict(self):
        """Convert JSON string back to dict"""
        try:
            return json.loads(self.enriched_info) if self.enriched_info else {}
        except:
            return {}
    
    def set_enriched_info_dict(self, info_dict):
        """Convert dict to JSON string"""
        self.enriched_info = json.dumps(info_dict)