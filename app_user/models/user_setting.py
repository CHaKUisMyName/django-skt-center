# -- สำหรับ map user เข้ากับ menu ระบบ
# -- แต่ละ App System จะมี class Setting เป็นของตัวเอง

from bson import ObjectId
import mongoengine as me

from base_models.settingbase import BaseSetting

class UserSetting(BaseSetting):
    id = me.ObjectIdField(primary_key= True, default= lambda: ObjectId())
    meta = {
        'collection': 'userSetting'  # 👈 ชื่อ collection ที่กำหนดเอง
    }