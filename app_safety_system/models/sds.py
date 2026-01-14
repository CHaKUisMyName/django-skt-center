from enum import Enum
from bson import ObjectId
import mongoengine as me
import datetime

from base_models.basemodel import BaseClass

class SdsType(Enum):
    Product = 1
    RawMaterial = 2
    Reagent = 3
    def serialize(self):
        return {
            "value": self.value,
            "label": self.name
        }

class SdsVersion(Enum):
    TH = (1, "Thai")
    EN = (2, "English")
    Gov = (3, "สอ.1")
    def __new__(cls, value, label):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.label = label
        return obj
    def serialize(self):
        return {
            "value": self.value,
            "label": self.label
        }

class SdsDocument(BaseClass):
    id = me.ObjectIdField(primary_key=True, default=lambda: ObjectId())
    # -- skt name fields --
    name = me.StringField(null=True, required=False, default=None)
    # -- chemical name fields --
    chemicalName = me.StringField(null=True, required=False, default=None)
    docPath = me.StringField(null=True, required=False, default=None)
    casNo = me.StringField(null=True, required=False, default=None)
    type = me.EnumField(SdsType)
    docVersion = me.EnumField(SdsVersion)
    isActive = me.BooleanField()
    note = me.StringField(null=True, required=False, default=None)

    meta = {
        'collection': 'sdsDocument'  # 👈 ชื่อ collection ที่กำหนดเอง
    }
    def serialize(self):
        return {
            "id": str(self.id),
            "name": self.name, # -- skt name --
            "chemicalName": self.chemicalName, # -- chemical name --
            "docPath": self.docPath,
            "casNo": self.casNo,
            "type": self.type.serialize() if self.type else None,
            "docVersion": self.docVersion.serialize() if self.docVersion else None,
            "isActive": self.isActive,
            "note": self.note,
            "createDate": self.createDate.astimezone(datetime.timezone.utc).isoformat() if self.createDate else None,
            "createBy": self.createBy.serialize() if self.createBy else None,
            "updateDate": self.updateDate.astimezone(datetime.timezone.utc).isoformat() if self.updateDate else None,
            "updateBy": self.updateBy.serialize() if self.updateBy else None,
        }