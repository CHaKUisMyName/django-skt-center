import mongoengine as me
from bson import ObjectId
import logging
from passlib.context import CryptContext

from app_user.models.user import User
from base_models.basemodel import BaseClass

# https://github.com/pyca/bcrypt/issues/684
#AttributeError: module 'bcrypt' has no attribute '__about__' with new 4.1.1 version #684
logging.getLogger('passlib').setLevel(logging.ERROR)

# สร้าง CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def VerifyPassword(password: str, hashPassword: str):
    return pwd_context.verify(password, hashPassword)

class AuthUser(BaseClass):
    id = me.ObjectIdField(primary_key= True, default= lambda: ObjectId())
    refUser = me.ReferenceField(User)
    userAuth = me.StringField(null= True, required= False, default = None)
    passWord = me.StringField(null= True, required= False, default = None)
    isActive = me.BooleanField(null= True, required= False, default = None)
    isDelete = me.BooleanField(null= True, required= False, default = None)
    note = me.StringField(null= True, required= False, default = None)
    lastLogin = me.DateTimeField(null= True, required= False, default = None)

    meta = {
        'collection': 'authUser'  # 👈 ชื่อ collection ที่กำหนดเอง
    }

    def hashPassword(self, password: str):
        self.passWord = pwd_context.hash(password)