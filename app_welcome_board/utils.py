import re
from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils import timezone
from datetime import timezone as dt_timezone
from urllib.parse import urljoin
from typing import List
from app_welcome_board.models.welcome_default import WelcomeBoardDefault
from app_welcome_board.models.welcome_guest import WelcomeBoardGuest
from app_welcome_board.models.welcomeboard import WelcomeBoardStatus


@sync_to_async
def get_all_welcome_data():
    welcome = WelcomeBoardGuest.objects.filter(isActive=True)
    serialized_paths = []
    for w in welcome:
        item = w.serialize()
        # ทำให้ path เป็น URL เต็ม
        item["path"] = urljoin(settings.MEDIA_URL, item["path"])
        # serialized_paths.append({"path": item["path"]})
        serialized_paths.append(item)
    return {
        "media_type": "image",
        "path": serialized_paths
    }


@sync_to_async
def get_filtered_welcome_data():
    now = timezone.now()
    # ถ้า MongoDB ใช้ UTC
    now_utc = now.astimezone(dt_timezone.utc)  # แปลงเป็น UTC
    welcome: List[WelcomeBoardGuest] = WelcomeBoardGuest.objects.filter(
        status=WelcomeBoardStatus.Show.value,
        isActive=True,
        sDate__lte=now_utc,
        eDate__gte=now_utc
    )
    if welcome:
        serialized_paths = []
        for w in welcome:
            item = w.serialize()
            item["path"] = urljoin(settings.MEDIA_URL, item["path"])
            # serialized_paths.append({"path": item["path"]})
            serialized_paths.append(item)
        return {
            "media_type": "image",
            "path": serialized_paths
        }

    # ถ้าไม่มี guest → ใช้ default
    default: WelcomeBoardDefault = WelcomeBoardDefault.objects.filter(isActive=True).first()
    if default:
        full_path = urljoin(settings.MEDIA_URL, default.path)
        return {
            "media_type": "video",
            "path": [{"path": full_path}]
        }

    # ถ้าไม่มีอะไรเลย → fallback image
    fallback_path = urljoin(settings.MEDIA_URL, "guest-img/skt-logo.png")
    return {
        "media_type": "image",
        "path": [{"path": fallback_path}]
    }


def sanitize_filename(filename: str) -> str:
    filename = filename.replace(" ", "_")
    filename = re.sub(r"[^A-Za-z0-9\.\-_]", "", filename)
    return filename
