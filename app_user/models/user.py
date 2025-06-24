import mongoengine as me
from bson import ObjectId
from enum import Enum

from base_models.basemodel import BaseClass

class UserStatus(Enum):
    Hire = 1
    Quit = 2
    Furlough = 3


class User(BaseClass):
    id = me.ObjectIdField(primary_key= True, default= lambda: ObjectId())
    code = me.StringField()
    fNameTH = me.StringField()
    lNameTH = me.StringField()
    fNameEN = me.StringField()
    lNameEN = me.StringField()
    nickName = me.StringField()
    nation = me.StringField()
    email = me.StringField()
    phone = me.StringField()
    birthDay = me.DateTimeField()
    status = me.EnumField(UserStatus)
    isAdmin = me.BooleanField()
    isActive = me.BooleanField()
    note = me.StringField()


    meta = {
        'collection': 'user'  # 👈 ชื่อ collection ที่กำหนดเอง
    }