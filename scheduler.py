from apscheduler.schedulers.background import BackgroundScheduler

from app_user.tasks import check_immigration_expired
from app_welcome_board.tasks import update_welcome_statuses


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_welcome_statuses, 'interval', seconds=5)  # ทุก 30 วินาที
    scheduler.add_job(check_immigration_expired, 'cron', hour=0, minute=0)

    scheduler.start()