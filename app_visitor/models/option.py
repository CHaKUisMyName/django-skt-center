from bson import ObjectId
import mongoengine as me
from base_models.basemodel import BaseClass


class Option(BaseClass):
    id = me.ObjectIdField(primary_key=True, default=lambda: ObjectId())
    name = me.StringField(null= True, required= False, default = None)
    note = me.StringField(null= True, required= False, default = None)
    isActive = me.BooleanField()

    meta = {
        'collection': 'visitorOption'  # 👈 ชื่อ collection ที่กำหนดเอง
    }

    def serialize(self):
        return {
            "id": str(self.id) if self.id else "",
            "name": self.name,
            "note": self.note,
            "isActive": self.isActive,
        }