from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

class DBConnection:
    def __init__(self):
        self.client = None
        self.db = None

    def connect(self):
        # TODO: Initialize Motor connection client in Milestone 2
        # self.client = AsyncIOMotorClient(settings.MONGODB_URL)
        # self.db = self.client.get_default_database()
        pass

    def disconnect(self):
        # TODO: Close database connection client in Milestone 2
        pass

db_connection = DBConnection()
