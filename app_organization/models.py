import mongoengine as me
from bson import ObjectId
from django.utils import timezone

from base_models.basemodel import BaseClass, UserSnapshot
from base_models.organizbase import BaseOrganization

class OrganizationSnapShot(me.EmbeddedDocument):
    id = me.ObjectIdField(default=ObjectId())
    code = me.StringField()
    nameTH = me.StringField()
    nameEN = me.StringField()
    shortName = me.StringField(null= True, required= False, default = None)
    parentCode = me.StringField(null= True, required= False, default = None)
    parentNameTH = me.StringField(null= True, required= False, default = None)
    parentNameEN = me.StringField(null= True, required= False, default = None)
    levelCode = me.StringField(null= True, required= False, default = None)
    LevelNameTH = me.StringField(null= True, required= False, default = None)
    levelNameEN = me.StringField(null= True, required= False, default = None)
    createDate = me.DateTimeField(default = timezone.now())
    createBy = me.EmbeddedDocumentField(UserSnapshot)

class Organization(BaseClass, BaseOrganization):
    id = me.ObjectIdField(primary_key=True, default=lambda: ObjectId())
    shortName = me.StringField(null= True, required= False, default = None)
    parent = me.ReferenceField('Organization', null= True, required= False, default = None)
    level = me.ReferenceField('Level', null= True, required= False, default = None)
    snapSots = me.EmbeddedDocumentListField(OrganizationSnapShot)

    meta = {
        'collection': 'organization'  # 👈 ชื่อ collection ที่กำหนดเอง
    }