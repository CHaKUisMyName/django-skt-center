from apscheduler.schedulers.background import BackgroundScheduler

from app_reminder.tasks import check_reminder
from app_user.tasks import check_immigration_expired
from app_user.utils import jobDeleteSessionExpired
from app_welcome_board.tasks import update_welcome_statuses


def start():
    scheduler = BackgroundScheduler()
    # # รันทุก 5 วินาที
    # scheduler.add_job(update_welcome_statuses, 'interval', seconds=5)
    # # รันทุกเที่ยงคืน
    # scheduler.add_job(check_immigration_expired, 'cron', hour=0, minute=0)
    # # ✅ รันทุกวันเวลา 02:00 (ตี 2)
    # scheduler.add_job(jobDeleteSessionExpired, 'cron', hour=2, minute=0)
    # # รันทุกเที่ยงคืน
    # scheduler.add_job(check_reminder, 'cron', hour=0, minute=0)

    scheduler.start()