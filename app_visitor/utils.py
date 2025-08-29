from bson import ObjectId
from app_visitor.models.visitor_setting import VisitorSetting


def HasVstPermission(id: str, menu: str = None, checkAdmin: bool = False):
    try:
        result = False
        vstSetting: VisitorSetting = VisitorSetting.objects.filter(user = ObjectId(id)).first()
        if vstSetting:
            if checkAdmin == True:
                if vstSetting.isAdmin == True and vstSetting.isActive == True:
                    result = True
            else:
                if vstSetting.isActive == True:
                    if menu:
                        result = any(m.name == menu for m in vstSetting.menus)
        return result
    except Exception as e:
        print(e)
        return False