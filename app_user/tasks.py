from django.utils import timezone
from datetime import timedelta, timezone as dt_timezone
from typing import List

import pytz

from app_user.models.immigration import ExpiredImmigration, Immigration
from app_user.utils import sendImmigration
from utilities.utility import printLogData

def check_immigration_expired():
    now = timezone.now()
    now_utc = now.astimezone(dt_timezone.utc)
    expired: List[Immigration] = Immigration.objects.filter(isActive=True)
    if expired and expired.count() > 0:
        for im in expired:
            dueDate = im.dueDate
            if dueDate and dueDate.tzinfo is None:  # ถ้าเป็น naive
                dueDate = dueDate.replace(tzinfo=pytz.UTC)
            diff = dueDate - now_utc
            if diff < timedelta(days=15) and diff > timedelta(days=7):
                printLogData(15)
                im.status = ExpiredImmigration.Befor15.value
                if im.hasNoti15 == False:
                    sendImmigration(im)
                    im.hasNoti15 = True
                im.save()
            if diff < timedelta(days=7) and diff > timedelta(days=0):
                printLogData(7)
                im.status = ExpiredImmigration.Befor7.value
                if im.hasNoti7 == False:
                    sendImmigration(im)
                    im.hasNoti7 = True
                im.save()
            if diff < timedelta(days=0) or diff == timedelta(days=0):
                printLogData(0)
                im.status = ExpiredImmigration.Expired.value
                if im.hasNotiExpired == False:
                    sendImmigration(im)
                    im.hasNotiExpired = True
                im.save()

            