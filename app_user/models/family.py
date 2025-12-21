from enum import Enum
import json
from typing import List
from bson import ObjectId
import mongoengine as me
from app_user.models.user import User
from base_models.basemodel import BaseClass, BaseEmbedded


class FamilyType(Enum):
    Father = 1
    Mother = 2
    Spouse = 3
    Children = 4
    def serialize(self):
        return {
            "value": self.value,
            "label": self.name
        }
    
class FamilyProfile(BaseEmbedded):
    fName = me.StringField()
    lName = me.StringField()
    relation = me.EnumField(FamilyType)
    note = me.StringField()
    
    def serialize(self):
        return {
            'fName': self.fName,
            'lName': self.lName,
            'note': self.note,
            'relation': self.relation.serialize() if self.relation else None,
        }
    
class UserFamily(BaseClass):
    id = me.ObjectIdField(primary_key= True, default= lambda: ObjectId())
    employee = me.ReferenceField(User)
    fatherProfile = me.EmbeddedDocumentField(FamilyProfile, default = None, null=True)
    motherProfile = me.EmbeddedDocumentField(FamilyProfile, default = None, null=True)
    spouseProfile = me.EmbeddedDocumentField(FamilyProfile, default = None, null=True)# -- คู่สมรส
    childrenProfile = me.EmbeddedDocumentListField(FamilyProfile, default = lambda: [])
    note = me.StringField()
    isActive = me.BooleanField()

    meta = {
        'collection': 'userFamily'  # 👈 ชื่อ collection ที่กำหนดเอง
    }

    def serialize(self):
        childrenProfile = []
        if self.childrenProfile:
            for child in self.childrenProfile:
                if child.fName or child.lName:
                    childrenProfile.append(child.serialize())
        return {
            'id': str(self.id),
            'employee': self.employee.serialize(),
            'fatherProfile': self.fatherProfile.serialize() if self.fatherProfile else None,
            'motherProfile': self.motherProfile.serialize() if self.motherProfile else None,
            'spouseProfile': self.spouseProfile.serialize() if self.spouseProfile else None,
            'childrenProfile': json.dumps(childrenProfile) if len(childrenProfile) > 0 else None,
            'note': self.note
        }
    
    def serialize_datatable(self):
        fatherProfile = self.fatherProfile.fName + " " + self.fatherProfile.lName if self.fatherProfile and (self.fatherProfile.fName or self.fatherProfile.lName) else "-"
        motherProfile = self.motherProfile.fName + " " + self.motherProfile.lName if self.motherProfile and (self.motherProfile.fName or self.motherProfile.lName) else "-"
        spouseProfile = self.spouseProfile.fName + " " + self.spouseProfile.lName if self.spouseProfile and (self.spouseProfile.fName or self.spouseProfile.lName) else "-"
        childrenProfile = []
        if self.childrenProfile:
            for child in self.childrenProfile:
                if child.fName or child.lName:
                    childrenProfile.append(child.fName + " " + child.lName)
        return {
            'id': str(self.id),
            'employee': self.employee.serialize(),
            'fatherProfile': fatherProfile,
            'fatherProfile_v2': self.fatherProfile if self.fatherProfile else "-",
            'motherProfile': motherProfile,
            'motherProfile_v2': self.motherProfile if self.motherProfile else "-",
            'spouseProfile': spouseProfile,
            'spouseProfile_v2': self.spouseProfile if self.spouseProfile else "-",
            'childrenProfile': json.dumps(childrenProfile) if len(childrenProfile) > 0 else "-",
            'childrenProfile_v2': self.childrenProfile if len(childrenProfile) > 0 else "-",
        }