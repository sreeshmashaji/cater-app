from typing import Optional
from pydantic import BaseModel


class ReviewInput(BaseModel):
    menuId:str
    restaurantId:str
    review:str
    starCount:Optional[float]=0
    
class ReviewLike(BaseModel):
    likeCount:Optional[int]=0
    dislikeCount:Optional[int]=0

class ReviewGet(BaseModel):
    menuId:str
    restaurantId:str

    
