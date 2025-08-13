from django import template

from app_organization.models.org_setting import OrgSetting
from app_user.models.user import User


register = template.Library()
@register.simple_tag
def has_menu_org(user: User, menu: str):
    if not user:
        return False
    if user.isAdmin == True:
        return True
    orgSetting: OrgSetting = OrgSetting.objects.filter(user = user.id).first()
    if not orgSetting or orgSetting.isActive == False:
        return False
    if orgSetting.isAdmin == True:
        return True
    return any(m.name == menu for m in orgSetting.menus)