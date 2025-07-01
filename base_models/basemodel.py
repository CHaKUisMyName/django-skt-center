import mongoengine as me
from django.utils import timezone

from utilities.utility import CheckStrEmpty

class UserSnapshot(me.EmbeddedDocument):
    uesrId = me.ObjectIdField()
    code = me.StringField()
    fullNameTH = me.StringField()
    fullNameEN = me.StringField()
    email = me.StringField()

    def UserToSnapshot(self, user):
        try:
            self.uesrId = user.id
            self.code = CheckStrEmpty(user.code)
            self.fullNameTH = CheckStrEmpty(user.fNameTH) + " " + CheckStrEmpty(user.lNameTH)
            self.fullNameEN = CheckStrEmpty(user.fNameEN) + " " + CheckStrEmpty(user.lNameEN)
            self.email = CheckStrEmpty(user.email)
            
            return self
        except Exception as e:
            print(e)
            return None

class BaseClass(me.Document):
    createDate = me.DateTimeField(default = timezone.now())
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