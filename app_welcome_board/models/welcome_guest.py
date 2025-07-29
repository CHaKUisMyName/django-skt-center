import mongoengine as me
from bson import ObjectId

from app_welcome_board.models.welcomeboard import WelcomeBoard

class WelcomeBoardGuest(WelcomeBoard):
    id = me.ObjectIdField(primary_key=True, default=lambda: ObjectId())
    
    meta = {
        'collection': 'welComeBoardGuest'
    }