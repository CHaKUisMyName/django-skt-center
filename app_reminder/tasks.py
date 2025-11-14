from datetime import timedelta, timezone as dt_timezone
from typing import List
from django.utils import timezone

from app_reminder.models.reminder import Reminder
from app_reminder.utils import sendMailReminder


def check_reminder():
    try:
        now = timezone.now()
        now_utc = now.astimezone(dt_timezone.utc)
        reminders: List[Reminder] = Reminder.objects.filter(isActive=True)
        if reminders and reminders.count() > 0:
            for r in reminders:
                expiredDate = r.expiredDate
                if expiredDate and expiredDate.tzinfo is None:  # ถ้าเป็น naive
                    expiredDate = expiredDate.replace(tzinfo=dt_timezone.utc)
                diff = expiredDate - now_utc
                # เตือนเมื่อเวลาที่เหลือน้อยกว่าหรือเท่ากับ alertBefore วัน
                if timedelta(days=r.alertBefore - 1) < diff <= timedelta(days=r.alertBefore):
                    print("⚠️ SEND REMINDER:", r.subject)
                    if not r.hasSendMail or r.hasSendMail == False:
                        hasSenMail = sendMailReminder(r)
                        r.hasSendMail = hasSenMail
                        r.status = True
                        r.save()
                    # -- TODO : send sms & set hasSendSms value
        return True
    except Exception as e:
        print(e)
        return False