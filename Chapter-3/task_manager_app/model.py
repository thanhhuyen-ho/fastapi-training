from pydantic import BaseModel

class Task(BaseModel):
    title: str
    description: str 
    status: str
    
class TaskWithID(Task):
    id: int
    
class TaskV2(BaseModel):
    title: str
    description: str
    status: str
    priority: str | None = "lower"
    
class TaskV2WithID(TaskV2):
    id: int
    
class User(BaseModel):
    username: str
    
class UserInDB(User):
    hashed_password: str
