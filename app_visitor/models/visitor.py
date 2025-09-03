from bson import ObjectId
import mongoengine as me
import pytz
import datetime

from app_visitor.models.room import Room
from base_models.basemodel import BaseClass

class Visitor(BaseClass):
    id = me.ObjectIdField(primary_key=True, default=lambda: ObjectId())
    topic = me.StringField(null= True, required= False, default = None)
    sDate = me.DateTimeField(null=True, required=False, default=None)
    eDate = me.DateTimeField(null=True, required=False, default=None)
    guestCompany = me.StringField(null=True, required=False, default=None)
    guestMember = me.StringField(null=True, required=False, default=None)
    sktMember = me.StringField(null=True, required=False, default=None)
    note = me.StringField(null=True, required=False, default=None)
    room = me.ReferenceField(Room, null=True, required=False, default=None)
    options = me.ListField(default=[])

    isActive = me.BooleanField()

    def clean(self):
        utc = pytz.UTC
        if self.sDate and self.sDate.tzinfo is None:
            self.sDate = self.sDate.replace(tzinfo=utc)
        if self.eDate and self.eDate.tzinfo is None:
            self.eDate = self.eDate.replace(tzinfo=utc)
    def serialize(self):
        return {
            "id": str(self.id),
            "topic": self.topic,
            "sDate": self.sDate.astimezone(datetime.timezone.utc).isoformat() if self.sDate else None,
            "eDate": self.eDate.astimezone(datetime.timezone.utc).isoformat() if self.eDate else None,
            "guestCompany": self.guestCompany,
            "guestMember": self.guestMember,
            "sktMember": self.sktMember,
            "roomId": str(self.room.id) if self.room else ",",
            "roomName": self.room.name if self.room else "",
            "roomColor": self.room.color if self.room else "",
            "note": self.note,
            "isActive": self.isActive,
            "createDate": self.createDate.astimezone(datetime.timezone.utc).isoformat() if self.createDate else None,
            "createBy":self.createBy.serialize() if self.createBy else None,
            "updateDate": self.updateDate.astimezone(datetime.timezone.utc).isoformat() if self.updateDate else None,
            "updateBy": self.updateBy.serialize() if self.updateBy else None,
        }
    meta = {
        'collection': 'visitor'  # 👈 ชื่อ collection ที่กำหนดเอง
    }