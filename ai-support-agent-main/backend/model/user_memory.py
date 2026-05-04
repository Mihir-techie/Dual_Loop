from pydantic import BaseModel

class Memory(BaseModel):
    user_id: str
    issue: str
    solution: str
    sentiment: str