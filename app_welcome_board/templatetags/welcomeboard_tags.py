from django import template

from app_user.models.user import User
from app_welcome_board.models.welcomboard_setting import WelcomeboardSetting

register = template.Library()
@register.simple_tag
def has_menu_welcomboard(user: User, menu: str):
    if not user:
        return False
    if user.isAdmin == True:
        return True
    wbSetting = WelcomeboardSetting.objects.filter(user = user).first()
    if not wbSetting or wbSetting.isActive == False:
        return False
    if wbSetting.isAdmin == True:
        return True
    return any(m.name == menu for m in wbSetting.menus)