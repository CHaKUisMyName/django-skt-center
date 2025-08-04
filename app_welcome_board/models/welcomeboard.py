from enum import Enum
import mongoengine as me
from datetime import datetime
from django.utils import timezone

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
    sDate = me.DateTimeField()
    eDate = me.DateTimeField()
    note = me.StringField(null=True, required=False, default=None)
    status = me.EnumField(WelcomeBoardStatus)
    isActive = me.BooleanField()

    meta = {'abstract': True}  # 👈 ต้องใส่เพื่อให้เป็น abstract class

    def clean(self):
        # ทำให้ sDate และ eDate เป็น timezone-aware
        tz = timezone.get_current_timezone()
        if self.sDate and self.sDate.tzinfo is None:
            self.sDate = timezone.make_aware(self.sDate, tz)
        if self.eDate and self.eDate.tzinfo is None:
            self.eDate = timezone.make_aware(self.eDate, tz)

    def serialize(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "path": self.path,
            "sDate": format_date(self.sDate),
            "eDate": format_date(self.eDate),
            "note": self.note,
            "status": format_enum(self.status),
            "isActive": self.isActive,
        
        }