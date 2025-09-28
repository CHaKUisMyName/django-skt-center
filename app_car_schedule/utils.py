from bson import ObjectId
from app_car_schedule.models.car_schedule_setting import CarScheduleSetting


def HasCshPermission(id: str, menu: str = None, checkAdmin: bool = False):
    try:
        result = False
        cshSetting: CarScheduleSetting = CarScheduleSetting.objects.filter(user = ObjectId(id)).first()
        if cshSetting:
            if checkAdmin == True:
                if cshSetting.isAdmin == True and cshSetting.isActive == True:
                    result = True
            else:
                if cshSetting.isActive == True:
                    if menu:
                        result = any(m.name == menu for m in cshSetting.menus)
        return result
    except Exception as e:
        print(e)
        return False