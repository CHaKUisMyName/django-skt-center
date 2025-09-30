import mongoengine as me
from bson import ObjectId

from base_models.settingbase import BaseSetting

class WelcomeboardSetting(BaseSetting):
    id = me.ObjectIdField(primary_key= True, default= lambda: ObjectId())
    meta = {
        'collection': 'welcomeboardSetting'  # 👈 ชื่อ collection ที่กำหนดเอง
    }