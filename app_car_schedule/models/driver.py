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

    meta = {
        'collection': 'carScheduleDriver'  # 👈 ชื่อ collection ที่กำหนดเอง
    }