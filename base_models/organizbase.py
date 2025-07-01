import mongoengine as me

class BaseOrganization:
    code = me.StringField()
    nameTH = me.StringField()
    nameEN = me.StringField()
    isActive = me.BooleanField()
    isDelete = me.BooleanField()
    note = me.StringField()
    
    meta = {'abstract': True}  # 👈 ต้องใส่เพื่อให้เป็น abstract class


