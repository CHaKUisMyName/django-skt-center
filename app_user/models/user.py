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
    orgNameEN = me.StringField()# -- snapshot ของ org name ไว้

    # -- เก็บ id เวลา load ทำการ lazy loading position จาก db
    posId = me.ReferenceField('app_position.models.position')
    posNameEN = me.StringField()# -- snapshot ของ position name ไว้

    isActive = me.BooleanField()
    isDelete = me.BooleanField()
    note = me.StringField()

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
    startJobDate = me.DateTimeField()
    status = me.EnumField(UserStatus)
    isAdmin = me.BooleanField()
    isActive = me.BooleanField()
    note = me.StringField()
    address = me.StringField()
    roles = me.EmbeddedDocumentListField(RoleUser)


    meta = {
        'collection': 'user'  # 👈 ชื่อ collection ที่กำหนดเอง
    }


