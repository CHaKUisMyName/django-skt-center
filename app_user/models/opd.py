from enum import Enum
from bson import ObjectId
import mongoengine as me
import datetime

from base_models.basemodel import BaseClass

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
        'collection': 'budgetOpd',
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
        'collection': 'optionOpd',
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