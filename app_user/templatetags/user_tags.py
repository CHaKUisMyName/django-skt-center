from django import template

from app_user.models.user import User
from app_user.models.user_setting import UserSetting

register = template.Library()

@register.simple_tag
def has_menu_user(user: User, menu: str):
    if not user:
        return False
    if user.isAdmin == True:
        return True
    userSetting: UserSetting = UserSetting.objects.filter(user = user.id).first()
    if not userSetting or userSetting.isActive == False:
        return False
    if userSetting.isAdmin == True:
        return True
    return any(m.name == menu for m in userSetting.menus)