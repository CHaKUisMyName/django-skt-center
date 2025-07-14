import mongoengine as me

from app_system_setting.models import SystemMenu
from app_user.models.user import User
from base_models.basemodel import BaseClass

class BaseSetting(BaseClass):
    user = me.ReferenceField(User)
    menus = me.ListField(me.ReferenceField(SystemMenu))
    isActive = me.BooleanField()
    isAdmin = me.BooleanField()
    note = me.StringField()
    meta = {'abstract': True}  # 👈 ต้องใส่เพื่อให้เป็น abstract class