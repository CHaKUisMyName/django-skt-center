from django import template

from app_user.models.user import User
from app_visitor.models.visitor_setting import VisitorSetting

register = template.Library()
@register.simple_tag
def has_menu_vst(user: User, menu: str):
    if not user:
        return False
    if user.isAdmin == True:
        return True
    vstSetting: VisitorSetting = VisitorSetting.objects.filter(user = user.id).first()
    if not vstSetting or vstSetting.isActive == False:
        return False
    if vstSetting.isAdmin == True:
        return True
    return any(m.name == menu for m in vstSetting.menus)