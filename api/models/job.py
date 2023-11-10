from typing import Optional
import motor
import motor.motor_asyncio
import os

from pydantic import BaseModel, Field, conlist
from api.models.message import Message

from api.models.object_id import PyObjectId


client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
db = client.api


class Job(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    api_key: Optional[str] = Field(None, description="The API key of the user who created this job.")
    messages: Optional[conlist(Message)] = Field(None, description="The message history of this job.")
