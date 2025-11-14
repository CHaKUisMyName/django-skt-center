from app_user.models.user import User
from base_models.basemodel import BaseClass
import mongoengine as me
from bson import ObjectId
import datetime


class Reminder(BaseClass):
    id = me.ObjectIdField(primary_key=True, default=lambda: ObjectId())
    subject = me.StringField(null=True, required=False, default=None)
    detail = me.StringField(null=True, required=False, default=None)
    receiver = me.ListField(me.StringField(), null=True, required=False, default=None)
    # fReceiver = me.ReferenceField(User, null=True, required=False, default=None)
    # sReceiver = me.ReferenceField(User, null=True, required=False, default=None)
    expiredDate = me.DateTimeField(null=True, required=False, default=None)
    # -- แจ้งเตือนล่วงหน้า นับเป็นวัน
    alertBefore = me.IntField(null=True, required=False, default=None)
    smsNumber = me.StringField(null=True, required=False, default=None)
    isSendMail = me.BooleanField(null=True, required=False, default=False)
    isSendSMS = me.BooleanField(null=True, required=False, default=False)
    hasSendMail = me.BooleanField(null=True, required=False, default=False)
    hasSendSms = me.BooleanField(null=True, required=False, default=False)
    note = me.StringField(null=True, required=False, default=None)
    status = me.BooleanField(null=True, required=False, default=True)
    isActive = me.BooleanField(null=True, required=False, default=True)

    meta = {
        'collection': 'reminder'  # 👈 ชื่อ collection ที่กำหนดเอง
    }

    def serialize(self):
        receivers = []
        if self.receiver:
            for r in self.receiver:
                user: User = User.objects.filter(id = ObjectId(r)).first()
                if user:
                    receivers.append(user.serialize())
        return {
            "id": str(self.id),
            "subject": self.subject,
            "detail": self.detail,
            "receiver": receivers,
            "expiredDate": self.expiredDate.astimezone(datetime.timezone.utc).isoformat() if self.expiredDate else None,
            "alertBefore": self.alertBefore,
            "smsNumber": self.smsNumber,
            "isSendMail": self.isSendMail,
            "isSendSMS": self.isSendSMS,
            "hasSendMail": self.hasSendMail,
            "hasSendSms": self.hasSendSms,
            "note": self.note,
            "status": self.status,
            "isActive": self.isActive,
            "createDate": self.createDate.astimezone(datetime.timezone.utc).isoformat() if self.createDate else None,
            "createBy": self.createBy.serialize() if self.createBy else None,
            "updateDate": self.updateDate.astimezone(datetime.timezone.utc).isoformat() if self.updateDate else None,
            "updateBy": self.updateBy.serialize() if self.updateBy else None,
        }
    
    def serailize_for_datatable(self):
        receivers = []
        if self.receiver:
            for r in self.receiver:
                user: User = User.objects.filter(id = ObjectId(r)).first()
                if user:
                    receivers.append(user.serialize())
        return {
            "id": str(self.id),
            "receiver": receivers,
            "details":{
                "subject": self.subject,
                "detail": self.detail,
                "expiredDate": self.expiredDate.astimezone(datetime.timezone.utc).isoformat() if self.expiredDate else None,
            },
            "options": {
                "isSendMail": self.isSendMail,
                "isSendSMS": self.isSendSMS,
            },
            "status": self.status,
        }
