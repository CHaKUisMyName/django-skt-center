import mongoengine as me
from bson import ObjectId
from enum import Enum

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
    passportNo = me.StringField(null= True, required= False, default = None)
    visaNo = me.StringField(null= True, required= False, default = None)
    workPermitNo = me.StringField(null= True, required= False, default = None)
    note = me.StringField(null= True, required= False, default = None)
    isActive = me.BooleanField(null= True, required= False, default = None)
    status = me.EnumField(ExpiredImmigration)

    meta = {
        'collection': 'immigration'  # 👈 ชื่อ collection ที่กำหนดเอง
    }