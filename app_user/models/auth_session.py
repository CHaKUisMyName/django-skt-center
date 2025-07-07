import base64
import json
import os
from dotenv import load_dotenv
import mongoengine as me
from cryptography.fernet import Fernet
from django.utils import timezone

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
cipher = Fernet(SECRET_KEY.encode())

class AuthSession(me.Document):
    session = me.StringField() # -- เก็บ session client
    token = me.StringField() # -- user data encrypt
    expireDate = me.DateTimeField() # -- เวลาหมดอายุของ session

    meta = {
        'collection': 'authSession'  # 👈 ชื่อ collection ที่กำหนดเอง
    }

    def SaveSessionData(self, data):
        """
        เข้ารหัสและบันทึก session_data
        param data: Dictionary ที่ต้องการเก็บใน session -> {"test": ...}
        """
        serializedData = json.dumps(data) # -- แปลงเป็น json
        encryptedData = cipher.encrypt(serializedData.encode()) # -- เข้ารหัส
        self.token = base64.urlsafe_b64encode(encryptedData).decode() # แปลงเป็น base 64 string for save to DB

    def GetSessionData(self):
        """
        ถอดรหัสและดึงข้อมูล session_data
        """
        try:
            encryptedData = base64.urlsafe_b64decode(self.token.encode())
            decryptedData = cipher.decrypt(encryptedData).decode()
            return json.loads(decryptedData)
        except Exception as e:
            print(str(e))
            return {}
    
    def DeleteSessionData(self):
        self.delete()

    def IsExpired(self):
        """
        ตรวจสอบว่า session หมดอายุหรือไม่
        return: True ถ้า session หมดอายุ
        """
        return timezone.now() > timezone.make_aware(self.expireDate)
    
    def ContinueSession(self):
        count = True if self.expireDate.date() == timezone.now().date() else False
        return count