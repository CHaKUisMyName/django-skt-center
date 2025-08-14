import re
from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils import timezone
from urllib.parse import urljoin
from typing import List
from app_welcome_board.models.welcome_default import WelcomeBoardDefault
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
        serialized_paths = []
        for w in welcome:
            item = w.serialize()
            # สร้าง URL เต็มโดยใช้ MEDIA_URL จาก settings
            item['path'] = urljoin(settings.MEDIA_URL, item['path'])
            serialized_paths.append(item)
        return {
            "media_type": "image",
            "path": serialized_paths
        }
    
    default: WelcomeBoardDefault = WelcomeBoardDefault.objects.filter(isActive=True).first()
    if default:
        # สร้าง URL เต็มสำหรับวิดีโอ
        full_path = urljoin(settings.MEDIA_URL, default.path)
        return {
            "media_type": "video",
            "path": {"path": full_path}
        }

    # สร้าง URL เต็มสำหรับรูปภาพสำรอง
    fallback_path = urljoin(settings.MEDIA_URL, "guest-img/skt-logo.png")
    return {
        "media_type": "image",
        "path": [{"path": fallback_path}]  # สำรองถ้าไม่มีรายการตรงเวลา
    }


def sanitize_filename(filename: str) -> str:
    # แทนช่องว่างด้วย -
    filename = filename.replace(' ', '-')
    # เอาอักขระที่ไม่ปลอดภัยออก (ยกเว้น .-_)
    filename = re.sub(r'[^A-Za-z0-9\.\-_]', '', filename)
    return filename