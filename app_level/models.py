import mongoengine as me
from bson import ObjectId
from django.utils import timezone

from base_models.basemodel import BaseClass, UserSnapshot
from base_models.organizbase import BaseOrganization

class LevelSnapShot(me.EmbeddedDocument):
    id = me.ObjectIdField(default=ObjectId())
    code = me.StringField()
    nameTH = me.StringField()
    nameEN = me.StringField()
    # เก็บ parent snapshot แทน parent จริง เพื่อให้ดูข้อมูลในอดีตได้
    parentCode = me.StringField(null= True, required= False, default = None)
    parentNameTH = me.StringField(null= True, required= False, default = None)
    parentNameEN = me.StringField(null= True, required= False, default = None)
    createDate = me.DateTimeField(default = timezone.now())
    createBy = me.EmbeddedDocumentField(UserSnapshot)



class Level(BaseClass, BaseOrganization):
    id = me.ObjectIdField(primary_key=True, default=lambda: ObjectId())
    parent = me.ReferenceField('Level', null= True, required= False, default = None)
    # -- # Snapshot ล่าสุด
    # lastSnapshot = me.EmbeddedDocumentField('LevelSnapshot', null=True)  # ← เก็บ snapshot ล่าสุดใน doc เดียวกัน

    # ประวัติ snapshot ทั้งหมด (optional)
    snapShots = me.EmbeddedDocumentListField(LevelSnapShot)  # ← อาจใช้หรือไม่ใช้ ขึ้นกับปริมาณ

    meta = {
        'collection': 'level'  # 👈 ชื่อ collection ที่กำหนดเอง
    }