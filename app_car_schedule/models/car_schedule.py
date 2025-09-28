from enum import Enum
import re
import mongoengine as me
from bson import ObjectId
import pytz
import datetime
from django.utils.timezone import make_aware
from base_models.basemodel import BaseClass

tz = pytz.timezone("Asia/Bangkok")

class ViewPersonCarSchedule(me.EmbeddedDocument):
    id = me.StringField(null=True, required=False, default=None)
    code = me.StringField(null=True, required=False, default=None)
    fNameEN = me.StringField(null=True, required=False, default=None)
    lNameEN = me.StringField(null=True, required=False, default=None)
    phone = me.StringField(null=True, required=False, default=None)
    email = me.StringField(null=True, required=False, default=None)
    carLicenseNo = me.StringField(null=True, required=False, default=None)

    @property
    def phone_thai(self):
        if not self.phone:
            return "-"
        digits = re.sub(r"\D", "", self.phone or "")
        if len(digits) == 10 and digits.startswith(("06", "08", "09")):
            return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
        if len(digits) == 9 and digits.startswith("02"):
            return f"{digits[:2]}-{digits[2:5]}-{digits[5:]}"
        return self.phone or "-"
    
    def serialize(self):
        return {
            "id": self.id,
            "code": self.code,
            "fNameEN": self.fNameEN,
            "lNameEN": self.lNameEN,
            "carLicenseNo": self.carLicenseNo,
            "phone": self.phone_thai,
            "email": self.email,
        }
    
class CarSchedule(BaseClass):
    id = me.ObjectIdField(primary_key=True, default=lambda: ObjectId())
    sDate = me.DateTimeField(null=True, required=False, default=None)
    eDate = me.DateTimeField(null=True, required=False, default=None)
    driver = me.EmbeddedDocumentField(ViewPersonCarSchedule)
    passengers = me.EmbeddedDocumentListField(ViewPersonCarSchedule, default = [])
    title = me.StringField(null= True, required= False, default = None)
    purpose = me.StringField(null= True, required= False, default = None)
    destination = me.StringField(null= True, required= False, default = None)
    color = me.StringField(null= True, required= False, default = None)
    isActive = me.BooleanField()

    meta = {
        'collection': 'carSchedule'  # 👈 ชื่อ collection ที่กำหนดเอง
    }
    def serialize(self, current_user=None, is_setting_admin=False):
        can_edit_delete = False
        if current_user:
            if getattr(current_user, "isAdmin", False) or is_setting_admin:
                can_edit_delete = True
            elif (self.createBy and str(self.createBy.userId) == str(current_user.id)) or \
                (self.updateBy and str(self.updateBy.userId) == str(current_user.id)):
                can_edit_delete = True
        return {
            "id": str(self.id) if self.id else "",
            # "sDate": self.sDate.strftime("%d/%m/%Y %H:%M") if self.sDate else "",
            # "eDate": self.eDate.strftime("%d/%m/%Y %H:%M") if self.eDate else "",
            "sDate": self.sDate.astimezone(datetime.timezone.utc).isoformat() if self.sDate else None,
            "eDate": self.eDate.astimezone(datetime.timezone.utc).isoformat() if self.eDate else None,
            "driver": self.driver.serialize() if self.driver else {},
            "passengers": [psg.serialize() for psg in self.passengers] if self.passengers else [],
            "title": self.title,
            "purpose": self.purpose,
            "destination": self.destination,
            "color": self.color,
            "isActive": self.isActive,
            "createDate": self.createDate.astimezone(datetime.timezone.utc).isoformat() if self.createDate else None,
            "createBy":self.createBy.serialize() if self.createBy else None,
            "updateDate": self.updateDate.astimezone(datetime.timezone.utc).isoformat() if self.updateDate else None,
            "updateBy": self.updateBy.serialize() if self.updateBy else None,
            "canEditDelete": can_edit_delete,
        }