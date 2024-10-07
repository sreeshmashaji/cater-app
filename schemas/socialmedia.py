from typing import Optional
from pydantic import BaseModel



class MediaLink(BaseModel):
    facebook:str|None=None
    instagram:str|None=None
    linkedin:str|None=None
    twitter:str|None=None
    



class LinkSave(BaseModel):
    ownerId:str
    links:MediaLink