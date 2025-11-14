from typing import List
from django.utils import timezone
from datetime import timezone as dt_timezone

from app_welcome_board.models.welcome_guest import WelcomeBoardGuest
from app_welcome_board.models.welcomeboard import WelcomeBoardStatus
from app_welcome_board.views import broadCastAllGuests, broadCastWelcomeBoard

# def update_welcome_statuses():
#     now = timezone.now()
#     now_utc = now.astimezone(dt_timezone.utc)
#     updated_count = 0

#     # เปลี่ยน Show → Showed
#     expired = WelcomeBoardGuest.objects.filter(
#         status=WelcomeBoardStatus.Show.value,
#         eDate__lt=now_utc,
#         isActive=True
#     )
#     for guest in expired:
#         guest.status = WelcomeBoardStatus.Showed
#         guest.save()
#         updated_count += 1

#     # เปลี่ยน Waiting → Show
#     ready = WelcomeBoardGuest.objects.filter(
#         status=WelcomeBoardStatus.Waiting.value,
#         sDate__lte=now_utc,
#         eDate__gte=now_utc,
#         isActive=True
#     )
#     for guest in ready:
#         guest.status = WelcomeBoardStatus.Show
#         guest.save()
#         updated_count += 1

#     if updated_count:
#         print(f"[Scheduler] Updated {updated_count} guest(s) status.")
#         broadCastAllGuests()
#         broadCastWelcomeBoard()

def update_welcome_statuses():
    now = timezone.now()
    now_utc = now.astimezone(dt_timezone.utc)

    # ✅ เปลี่ยน Show → Showed (bulk update)
    changed_show_to_showed = WelcomeBoardGuest.objects(
        status=WelcomeBoardStatus.Show.value,
        eDate__lt=now_utc,
        isActive=True
    ).update(status=WelcomeBoardStatus.Showed.value)

    # ✅ เปลี่ยน Waiting → Show (bulk update)
    changed_waiting_to_show = WelcomeBoardGuest.objects(
        status=WelcomeBoardStatus.Waiting.value,
        sDate__lte=now_utc,
        eDate__gte=now_utc,
        isActive=True
    ).update(status=WelcomeBoardStatus.Show.value)

    updated_count = changed_show_to_showed + changed_waiting_to_show

    if updated_count > 0:
        print(f"[Scheduler] Updated {updated_count} guest(s) status.")
        broadCastAllGuests()
        broadCastWelcomeBoard()