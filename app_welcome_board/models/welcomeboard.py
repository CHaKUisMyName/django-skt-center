from enum import Enum
import mongoengine as me
from datetime import datetime
from django.utils.timezone import localtime, make_aware, get_current_timezone
import pytz
import datetime

from base_models.basemodel import BaseClass

class WelcomeBoardStatus(Enum):
    Waiting = 1
    Show = 2
    Showed = 3

def format_date(dt):
    if isinstance(dt, datetime):
        return dt.strftime("%d-%m-%Y %H:%M")
    return str(dt) if dt else None

def format_enum(e):
    if isinstance(e, Enum):
        return e.name
    return str(e) if e else None
    
class WelcomeBoard(BaseClass):
    title = me.StringField(null=True, required=False, default=None)
    path = me.StringField(null=True, required=False, default=None)
    sDate = me.DateTimeField(null=True, required=False, default=None)
    eDate = me.DateTimeField(null=True, required=False, default=None)
    note = me.StringField(null=True, required=False, default=None)
    status = me.EnumField(WelcomeBoardStatus)
    isActive = me.BooleanField()

    meta = {'abstract': True}  # 👈 ต้องใส่เพื่อให้เป็น abstract class

    def clean(self):
        utc = pytz.UTC
        if self.sDate and self.sDate.tzinfo is None:
            self.sDate = self.sDate.replace(tzinfo=utc)
        if self.eDate and self.eDate.tzinfo is None:
            self.eDate = self.eDate.replace(tzinfo=utc)

    def serialize(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "path": self.path,
            "sDate": self.sDate.astimezone(datetime.timezone.utc).isoformat() if self.sDate else None,
            "eDate": self.eDate.astimezone(datetime.timezone.utc).isoformat() if self.eDate else None,
            "note": self.note,
            "status": {
                "name": self.status.name if self.status else None,
                "value": self.status.value if self.status else None,
            },
            "isActive": self.isActive,
            "createDate": self.createDate.astimezone(datetime.timezone.utc).isoformat() if self.createDate else None,
            "createBy":self.createBy.serialize() if self.createBy else None,
            "updateDate": self.updateDate.astimezone(datetime.timezone.utc).isoformat() if self.updateDate else None,
            "updateBy": self.updateBy.serialize() if self.updateBy else None,
        }
    
def safe_localtime(dt):
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = make_aware(dt, get_current_timezone())
    return localtime(dt)