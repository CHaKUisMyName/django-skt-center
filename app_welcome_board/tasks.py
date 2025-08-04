from django.utils import timezone

from app_welcome_board.models.welcome_guest import WelcomeBoardGuest
from app_welcome_board.models.welcomeboard import WelcomeBoardStatus
from app_welcome_board.views import broadCastWelcomeBoard

def update_welcome_statuses():
    now = timezone.now()
    updated_count = 0

    # ✅ เปลี่ยนจาก Show → Showed ถ้าเลยเวลา
    expired = WelcomeBoardGuest.objects.filter(
        status=WelcomeBoardStatus.Show,
        eDate__lt=now,
        isActive=True
    )
    for guest in expired:
        guest.status = WelcomeBoardStatus.Showed.value
        guest.save()
        updated_count += 1

    # ✅ เปลี่ยนจาก Waiting → Show ถ้าอยู่ในช่วงเวลา
    ready = WelcomeBoardGuest.objects.filter(
        status=WelcomeBoardStatus.Waiting,
        sDate__lte=now,
        eDate__gte=now,
        isActive=True
    )
    for guest in ready:
        guest.status = WelcomeBoardStatus.Show.value
        guest.save()
        updated_count += 1

    if updated_count:
        print(f"[Scheduler] Updated {updated_count} guest(s) status.")
        broadCastWelcomeBoard()