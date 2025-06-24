import mongoengine as me
from bson import ObjectId
from django.utils import timezone


from base_models.basemodel import BaseClass, UserSnapshot
from base_models.organizbase import BaseOrganization

class PositionSnapShot(me.EmbeddedDocument):
    id = me.ObjectIdField(default=ObjectId())
    code = me.StringField()
    nameTH = me.StringField()
    nameEN = me.StringField()
    parentCode = me.StringField(null= True, required= False, default = None)
    parentNameTH = me.StringField(null= True, required= False, default = None)
    parentNameEN = me.StringField(null= True, required= False, default = None)
    createDate = me.DateTimeField(default = timezone.now())
    createBy = me.EmbeddedDocumentField(UserSnapshot)


class Position(BaseClass, BaseOrganization):
    id = me.ObjectIdField(primary_key=True, default=lambda: ObjectId())
    parent = me.ReferenceField('Position', null= True, required= False, default = None)
    snapShots = me.EmbeddedDocumentListField(PositionSnapShot)
    
    meta = {
        'collection': 'position'  # 👈 ชื่อ collection ที่กำหนดเอง
    }

    def serialize_position(self):
        # -- เอา element ตัวสุดท้ายของลิสต์นี้ (ตำแหน่งล่าสุดที่เพิ่มเข้ามา)
        # latest_snap = self.snapShots[-1] if self.snapShots else None
        data = {
            "id": str(self.id),
            "code": self.code,
            "nameTH": self.nameTH,
            "nameEN": self.nameEN,
            "parentId": str(self.parent.id) if self.parent else None,
            "parentCode": self.parent.code if self.parent else None,
            "parentNameTH": self.parent.nameTH if self.parent else None,
            "parentNameEN": self.parent.nameEN if self.parent else None,
        }
        return data