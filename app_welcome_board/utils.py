from asgiref.sync import sync_to_async
from django.utils import timezone
from typing import List
from app_welcome_board.models.welcome_guest import WelcomeBoardGuest
from app_welcome_board.models.welcomeboard import WelcomeBoardStatus

@sync_to_async
def get_all_welcome_data():
    welcome = WelcomeBoardGuest.objects.filter(isActive=True)
    return {
        "media_type": "image",
        "path": [w.serialize() for w in welcome]
    }

@sync_to_async
def get_filtered_welcome_data():
    now = timezone.now()
    welcome: List[WelcomeBoardGuest] = WelcomeBoardGuest.objects.filter(
        status=WelcomeBoardStatus.Show,
        isActive=True,
        sDate__lte=now,
        eDate__gte=now
    )
    if welcome:
        return {
            "media_type": "image",
            "path": [w.serialize() for w in welcome]
        }
    return {
        "media_type": "video",
        "path": [{"path": "guest-img/senikame-2.jpg"}]  # สำรองถ้าไม่มีรายการตรงเวลา
    }
