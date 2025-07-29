from enum import Enum
import mongoengine as me

from base_models.basemodel import BaseClass

class WelcomeBoardStatus(Enum):
    Waiting = 1
    Show = 2
    Showed = 3
    
class WelcomeBoard(BaseClass):
    title = me.StringField(null=True, required=False, default=None)
    path = me.StringField(null=True, required=False, default=None)
    sDate = me.DateTimeField()
    eDate = me.DateTimeField()
    note = me.StringField(null=True, required=False, default=None)
    status = me.EnumField(WelcomeBoardStatus)
    isActive = me.BooleanField()

    meta = {'abstract': True}  # 👈 ต้องใส่เพื่อให้เป็น abstract class