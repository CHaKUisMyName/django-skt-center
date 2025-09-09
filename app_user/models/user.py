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

class EmpNation(Enum):
    Thai = 1
    Japan = 2
    China = 3
    Korea = 4
    Vietnam = 5

class UserType(Enum):
    Employee = 1
    SubContract = 2
    Intern = 3


class RoleUser(BaseEmbedded):
    # -- เก็บ id เวลา load ทำการ lazy loading org จาก db
    # -- แต่เวลา python load ขั้นมาจะเป็น object
    orgId = me.ReferenceField('app_organization.models.Organization')
    orgNameEN = me.StringField(null= True, required= False, default = None)# -- snapshot ของ org name ไว้

    # -- เก็บ id เวลา load ทำการ lazy loading position จาก db
    posId = me.ReferenceField('app_position.models.Position')
    posNameEN = me.StringField(null= True, required= False, default = None)# -- snapshot ของ position name ไว้

    isActive = me.BooleanField(null= True, required= False, default = None)
    isDelete = me.BooleanField(null= True, required= False, default = None)
    note = me.StringField(null= True, required= False, default = None)

    def serialize(self):
        return {
            "orgId": str(self.orgId.id),
            "orgNameEN": self.orgNameEN,
            "posId": str(self.posId.id),
            "posNameEN": self.posNameEN,
            "isActive": self.isActive,
            "isDelete": self.isDelete,
            "note": self.note
        }

class User(BaseClass):
    id = me.ObjectIdField(primary_key= True, default= lambda: ObjectId())
    code = me.StringField()
    fNameTH = me.StringField(null= True, required= False, default = None)
    lNameTH = me.StringField(null= True, required= False, default = None)
    fNameEN = me.StringField()
    lNameEN = me.StringField()
    nickName = me.StringField(null= True, required= False, default = None)
    # nation = me.StringField(null= True, required= False, default = None)
    nation = me.EnumField(EmpNation)
    email = me.StringField(null= True, required= False, default = None)
    phone = me.StringField(null= True, required= False, default = None)
    birthDay = me.DateTimeField(null= True, required= False, default = None)
    startJobDate = me.DateTimeField()
    status = me.EnumField(UserStatus)
    userType = me.EnumField(UserType)
    isAdmin = me.BooleanField()
    isActive = me.BooleanField()
    isDelete = me.BooleanField(null= True, required= False, default = None)
    isRegister = me.BooleanField(null= True, required= False, default = None)
    note = me.StringField(null= True, required= False, default = None)
    address = me.StringField(null= True, required= False, default = None)
    roles = me.EmbeddedDocumentListField(RoleUser)

    meta = {
        'collection': 'user'  # 👈 ชื่อ collection ที่กำหนดเอง
    }

    def serialize(self):
        return {
            "id": str(self.id),
            "code": self.code,
            "fNameTH": self.fNameTH,
            "lNameTH": self.lNameTH,
            "fNameEN": self.fNameEN,
            "lNameEN": self.lNameEN,
            "nickName": self.nickName,
            "nation": self.nation.name if self.nation else None,
            "email": self.email,
            "phone": self.phone,
            "birthDay": self.birthDay.strftime("%Y-%m-%d") if self.birthDay else None,
            "startJobDate": self.startJobDate.strftime("%Y-%m-%d") if self.startJobDate else None,
            "status": self.status.name if self.status else None,  # <-- แปลง Enum เป็น string
            "userType": self.userType.name if self.userType else None,  # <-- แปลง Enum เป็น string
            "isAdmin": self.isAdmin,
            "isActive": self.isActive,
            "isDelete": self.isDelete,
            "isRegister": self.isRegister,
            "note": self.note,
            "address": self.address,
            "roles": [role.serialize() for role in self.roles],  # <-- เรียก serialize จาก RoleUser
        }


