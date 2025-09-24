import mongoengine as me
from bson import ObjectId
from base_models.basemodel import BaseClass


class Car(BaseClass):
    id = me.ObjectIdField(primary_key=True, default=lambda: ObjectId())
    brand = me.StringField(null= True, required= False, default = None)
    model = me.StringField(null= True, required= False, default = None)
    licenseNo = me.StringField(null= True, required= False, default = None)
    note = me.StringField(null= True, required= False, default = None)
    isActive = me.BooleanField()

    meta = {
        'collection': 'carScheduleCar'  # 👈 ชื่อ collection ที่กำหนดเอง
    }

    def serialize(self):
        return {
            "id": str(self.id) if self.id else "",
            "brand": self.brand,
            "model": self.model,
            "licenseNo": self.licenseNo,
            "note": self.note,
            "isActive": self.isActive,
        }