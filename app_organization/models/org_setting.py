import mongoengine as me
from bson import ObjectId

from base_models.settingbase import BaseSetting

class OrgSetting(BaseSetting):
    id = me.ObjectIdField(primary_key= True, default= lambda: ObjectId())
    meta = {
        'collection': 'orgSetting'  # 👈 ชื่อ collection ที่กำหนดเอง
    }