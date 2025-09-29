import mongoengine as me
from bson import ObjectId

from app_car_schedule.models.car import Car
from app_user.models.user import User
from base_models.basemodel import BaseClass

class Driver(BaseClass):
    id = me.ObjectIdField(primary_key= True, default= lambda: ObjectId())
    user = me.ReferenceField(User, null=True, required=False, default=None)
    car = me.ReferenceField(Car, null=True, required=False, default=None)
    color = me.StringField(null= True, required= False, default = None)
    note = me.StringField(null= True, required= False, default = None)
    isActive = me.BooleanField()
    @property
    def fullNameEN(self):
        if not self.user:
            return "-"
        code  = self.user.code if self.user.code else "-"
        fNameEN = self.user.fNameEN if self.user.fNameEN else ""
        lNameEN = self.user.lNameEN if self.user.lNameEN else ""
        return f"({code}) {fNameEN} {lNameEN}"
    
    def serialize(self):
        return {
            "id": str(self.id) if self.id else "",
            "fullNameEN": self.fullNameEN,
            "user": self.user.serialize() if self.user else {},
            "car": self.car.serialize() if self.car else {},
            "color": self.color,
            "note": self.note,
            "isActive": self.isActive,
        }


    meta = {
        'collection': 'carScheduleDriver'  # 👈 ชื่อ collection ที่กำหนดเอง
    }