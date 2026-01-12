from django import template

from app_safety_system.models.safety_setting import SafetySetting
from app_user.models.user import User

register = template.Library()

@register.simple_tag
def has_menu_safety(user: User, menu: str):
    if not user:
        return False
    if user.isAdmin == True:
        return True
    print(user.id)
    safetySetting: SafetySetting = SafetySetting.objects.filter(user=user.id).first()
    if not safetySetting or safetySetting.isActive == False:
        return False
    if safetySetting.isAdmin == True:
        return True
    return any(m.name == menu for m in safetySetting.menus)