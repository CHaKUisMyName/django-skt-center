# -- check ว่า user login นี้เป็น admin สำหรับชุดเมนู organization หรือไม่ ?
from bson import ObjectId

from app_organization.models.org_setting import OrgSetting


def isSettingOrgAdmin(id):
    try:
        result = False
        orgSetting: OrgSetting = OrgSetting.objects.filter(user = ObjectId(id), isActive = True).first()
        if orgSetting:
            if orgSetting.isAdmin == True:
                result = True
        return result

    except Exception as e:
        print(e)
        return False