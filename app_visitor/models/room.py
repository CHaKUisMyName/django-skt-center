from bson import ObjectId
import mongoengine as me
from base_models.basemodel import BaseClass


class Room(BaseClass):
    id = me.ObjectIdField(primary_key=True, default=lambda: ObjectId())
    name = me.StringField(null= True, required= False, default = None)
    note = me.StringField(null= True, required= False, default = None)
    isActive = me.BooleanField()

    meta = {
        'collection': 'visitorRoom'  # 👈 ชื่อ collection ที่กำหนดเอง
    }