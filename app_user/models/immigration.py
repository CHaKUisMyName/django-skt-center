import mongoengine as me
from bson import ObjectId
from enum import Enum
import pytz
import datetime

from app_user.models.user import User
from base_models.basemodel import BaseClass

class ExpiredImmigration(Enum):
    Normal = 1
    Befor15 = 2
    Befor7 = 3
    Expired = 4

class Immigration(BaseClass):
    id = me.ObjectIdField(primary_key= True, default= lambda: ObjectId())
    refUser = me.ReferenceField(User)
    dueDate = me.DateTimeField(null=True, required=False, default=None)
    inputDate = me.DateTimeField(null=True, required=False, default=None)
    note = me.StringField(null= True, required= False, default = None)
    isActive = me.BooleanField(null= True, required= False, default = None)
    status = me.EnumField(ExpiredImmigration)
    hasNoti15 = me.BooleanField(null= True, required= False, default = None)
    hasNoti7 = me.BooleanField(null= True, required= False, default = None)
    hasNotiExpired = me.BooleanField(null= True, required= False, default = None)

    def serialize(self):
        return {
            "id": str(self.id),
            "refUser": self.refUser.serialize() if self.refUser else {},
            "dueDate": self.dueDate.astimezone(datetime.timezone.utc).isoformat() if self.dueDate else None,
            "inputDate": self.inputDate.astimezone(datetime.timezone.utc).isoformat() if self.inputDate else None,
            "note": self.note,
            "isActive": self.isActive,
            # "status": self.status if self.status else None,
            "status": {
                "name": self.status.name,
                "value": self.status.value
            } if self.status else None,
            "hasNoti15": self.hasNoti15,
            "hasNoti7": self.hasNoti7,
            "hasNotiExpired": self.hasNotiExpired,
        }


    meta = {
        'collection': 'immigration'  # 👈 ชื่อ collection ที่กำหนดเอง
    }