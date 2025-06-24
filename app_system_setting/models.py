# from django.db import models
import mongoengine as me
from bson import ObjectId

from base_models.basemodel import BaseClass

class SystemApp(BaseClass):
    id = me.ObjectIdField(primary_key=True, default=lambda: ObjectId())
    name = me.StringField()
    isActive = me.BooleanField()
    note = me.StringField()
    
    meta = {
        'collection': 'systemApp'  # 👈 ชื่อ collection ที่กำหนดเอง
    }


class SystemMenu(BaseClass):
    id = me.ObjectIdField(primary_key=True, default=lambda: ObjectId())
    name = me.StringField()
    app = me.ReferenceField(SystemApp)
    isActive = me.BooleanField()
    note = me.StringField()
    
    meta = {
        'collection': 'systemMenu'  # 👈 ชื่อ collection ที่กำหนดเอง
    }