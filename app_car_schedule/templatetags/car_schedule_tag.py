from django import template

from app_car_schedule.models.car_schedule_setting import CarScheduleSetting
from app_user.models.user import User


register = template.Library()
@register.simple_tag
def has_menu_csh(user: User, menu: str):
    if not user:
        return False
    if user.isAdmin == True:
        return True
    cshSetting: CarScheduleSetting = CarScheduleSetting.objects.filter(user = user.id).first()
    if not cshSetting or cshSetting.isActive == False:
        return False
    if cshSetting.isAdmin == True:
        return True
    return any(m.name == menu for m in cshSetting.menus)