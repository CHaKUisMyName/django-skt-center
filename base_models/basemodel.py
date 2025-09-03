import datetime
import mongoengine as me
from django.utils import timezone

class UserSnapshot(me.EmbeddedDocument):
    userId = me.ObjectIdField()
    code = me.StringField()
    fullNameTH = me.StringField()
    fullNameEN = me.StringField()
    email = me.StringField()

    def UserToSnapshot(self, user):
        try:
            self.userId = user.id
            self.code = user.code or ""
            self.fullNameTH = f"{user.fNameTH or ''} {user.lNameTH or ''}".strip()
            self.fullNameEN = f"{user.fNameEN or ''} {user.lNameEN or ''}".strip()
            self.email = user.email or ""
            
            return self
        except Exception as e:
            print(e)
            return None
    def serialize(self):
        return {
            "userId": str(self.userId),
            "code": self.code,
            "fullNameTH": self.fullNameTH,
            "fullNameEN": self.fullNameEN,
            "email": self.email,
        }

class BaseClass(me.Document):
    createDate = me.DateTimeField(default = timezone.now)
    createBy = me.EmbeddedDocumentField(UserSnapshot)
    updateDate = me.DateTimeField()
    updateBy = me.EmbeddedDocumentField(UserSnapshot)
    meta = {'abstract': True}  # 👈 ต้องใส่เพื่อให้เป็น abstract class

# - เอาสำหรับใช้ embedded ใน class
class BaseEmbedded(me.EmbeddedDocument):
    createDate = me.DateTimeField()
    createBy = me.EmbeddedDocumentField(UserSnapshot)
    updateDate = me.DateTimeField()
    updateBy = me.EmbeddedDocumentField(UserSnapshot)
    meta = {'abstract': True}  # 👈 ต้องใส่เพื่อให้เป็น abstract class