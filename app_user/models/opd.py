from enum import Enum
from bson import ObjectId
import mongoengine as me
import datetime

from app_user.models.family import FamilyProfile
from app_user.models.user import User
from base_models.basemodel import BaseClass, BaseEmbedded

class OpdType(Enum):
    Employee = 1
    Family = 2

class BudgetEmpType(Enum):
    Thai = 1
    Foreigner = 2

class BudgetOpd(BaseClass):
    id = me.ObjectIdField(primary_key= True, default= lambda: ObjectId())
    type = me.EnumField(BudgetEmpType)
    year = me.StringField(null= True, required= False, default = None)
    budget = me.FloatField(null= True, required= False, default = None)
    status = me.BooleanField(null= True, required= False, default = None)
    isActive = me.BooleanField()

    meta = {
        'collection': 'opdBudget',
    }

    def serialize(self):
        return {
            "id": str(self.id),
            "year": self.year,
            "budget": self.budget,
            "status": self.status,
            "isActive": self.isActive,
            "createDate": self.createDate.astimezone(datetime.timezone.utc).isoformat() if self.createDate else None,
            "createBy": self.createBy.serialize() if self.createBy else None,
            "updateDate": self.updateDate.astimezone(datetime.timezone.utc).isoformat() if self.updateDate else None,
            "updateBy": self.updateBy.serialize() if self.updateBy else None,
        }
    
class OptionOpd(BaseClass):
    id = me.ObjectIdField(primary_key= True, default= lambda: ObjectId())
    name = me.StringField(null= True, required= False, default = None)
    status = me.BooleanField(null= True, required= False, default = None)
    isActive = me.BooleanField()
    description = me.StringField(null= True, required= False, default = None)
    useTypes = me.ListField(me.EnumField(OpdType), null=True, required=False, default=None)

    meta = {
        'collection': 'opdOption',
    }

    def serialize(self):
        useTypes = []
        if self.useTypes:
            for ut in self.useTypes:
                useTypes.append({
                    "name": ut.name,
                    "value": ut.value
                })
        return {
            "id": str(self.id),
            "name": self.name,
            "status": self.status,
            "isActive": self.isActive,
            "description": self.description,
            "useTypes": useTypes,
            "createDate": self.createDate.astimezone(datetime.timezone.utc).isoformat() if self.createDate else None,
            "createBy": self.createBy.serialize() if self.createBy else None,
            "updateDate": self.updateDate.astimezone(datetime.timezone.utc).isoformat() if self.updateDate else None,
            "updateBy": self.updateBy.serialize() if self.updateBy else None,
        }
    
class DisbursementOpd(BaseEmbedded):
    type = me.EnumField(OpdType)
    refOption = me.ReferenceField(OptionOpd)
    familyMember = me.EmbeddedDocumentField(FamilyProfile, null= True, required= False, default = None)
    amount = me.FloatField(null= True, required= False, default = None)
    def serialize(self):
        
        return {
            "type": self.type.name if self.type else None,
            "refOption": self.refOption.serialize() if self.refOption else None,
            "familyMember": self.familyMember.serialize() if self.familyMember else None,
            "amount": self.amount,
        }
    
class OPDRecord(BaseClass):
    id = me.ObjectIdField(primary_key= True, default= lambda: ObjectId())
    employee = me.ReferenceField(User)
    inputDate = me.DateTimeField(null=True, required=False, default=None)
    hospital = me.StringField(null=True, required=False, default=None)
    totalAmount = me.FloatField(null= True, required= False, default = None)
    disbursements = me.EmbeddedDocumentListField(DisbursementOpd, default = lambda: [])
    note = me.StringField(null= True, required= False, default = None)
    isActive = me.BooleanField()

    meta = {
        'collection': 'opdRecord',
    }

    def serialize(self):
        disbursements = []
        if self.disbursements:
            for dis in self.disbursements:
                if dis:
                    disbursements.append(dis.serialize())
        return {
            "id": str(self.id),
            "employee": self.employee.serialize() if self.employee else None,
            "inputDate": self.inputDate.astimezone(datetime.timezone.utc).isoformat() if self.inputDate else None,
            # "inputDate": self.inputDate.strftime("%Y-%m-%d") if self.inputDate else None,
            "totalAmount": self.totalAmount,
            "hospital": self.hospital,
            "disbursements": disbursements,
            "note": self.note,
            "isActive": self.isActive,
            "createDate": self.createDate.astimezone(datetime.timezone.utc).isoformat() if self.createDate else None,
            "createBy": self.createBy.serialize() if self.createBy else None,
            "updateDate": self.updateDate.astimezone(datetime.timezone.utc).isoformat() if self.updateDate else None,
            "updateBy": self.updateBy.serialize() if self.updateBy else None,
        }