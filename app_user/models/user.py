import mongoengine as me
from bson import ObjectId
from enum import Enum

from base_models.basemodel import BaseClass, BaseEmbedded


class UserStatus(Enum):
    Hire = 1
    Quit = 2
    Furlough = 3
    Retired = 4
    LayOff = 5

class RoleUser(BaseEmbedded):
    # -- เก็บ id เวลา load ทำการ lazy loading org จาก db
    orgId = me.ReferenceField('app_organization.models.Organization')
    orgNameEN = me.StringField(null= True, required= False, default = None)# -- snapshot ของ org name ไว้

    # -- เก็บ id เวลา load ทำการ lazy loading position จาก db
    posId = me.ReferenceField('app_position.models.Position')
    posNameEN = me.StringField(null= True, required= False, default = None)# -- snapshot ของ position name ไว้

    isActive = me.BooleanField(null= True, required= False, default = None)
    isDelete = me.BooleanField(null= True, required= False, default = None)
    note = me.StringField(null= True, required= False, default = None)

class User(BaseClass):
    id = me.ObjectIdField(primary_key= True, default= lambda: ObjectId())
    code = me.StringField()
    fNameTH = me.StringField(null= True, required= False, default = None)
    lNameTH = me.StringField(null= True, required= False, default = None)
    fNameEN = me.StringField()
    lNameEN = me.StringField()
    nickName = me.StringField(null= True, required= False, default = None)
    nation = me.StringField(null= True, required= False, default = None)
    email = me.StringField(null= True, required= False, default = None)
    phone = me.StringField(null= True, required= False, default = None)
    birthDay = me.DateTimeField(null= True, required= False, default = None)
    startJobDate = me.DateTimeField()
    status = me.EnumField(UserStatus)
    isAdmin = me.BooleanField()
    isActive = me.BooleanField()
    isRegister = me.BooleanField(null= True, required= False, default = None)
    note = me.StringField(null= True, required= False, default = None)
    address = me.StringField(null= True, required= False, default = None)
    roles = me.EmbeddedDocumentListField(RoleUser)


    meta = {
        'collection': 'user'  # 👈 ชื่อ collection ที่กำหนดเอง
    }


