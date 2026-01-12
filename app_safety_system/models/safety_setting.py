from bson import ObjectId
import mongoengine as me
from base_models.settingbase import BaseSetting


class SafetySetting(BaseSetting):
    id = me.ObjectIdField(primary_key= True, default= lambda: ObjectId())
    meta = {
        'collection': 'safetySetting'
    }