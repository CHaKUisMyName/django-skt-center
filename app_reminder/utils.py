from zoneinfo import ZoneInfo
from bson import ObjectId
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from app_reminder.models.reminder import Reminder
from app_user.models.user import User


def sendMailReminder(reminder: Reminder):
    try:
        if not reminder:
            return False
        
        if not reminder.receiver:
            return False
        
        # listEmail = [r.email for r in reminder.receiver]
        listEmail = []
        for r in reminder.receiver:
            user = User.objects.filter(id = ObjectId(r)).first()
            if user:
                listEmail.append(user.email)
        print(listEmail)
        if not listEmail or len(listEmail) == 0:
            return False
        
        to_email = listEmail

        # -- แปลง datetime UTC เป็น thai datetime format dd/mm/yyyy
        expiredDateTH = reminder.expiredDate.astimezone(ZoneInfo("Asia/Bangkok")).strftime("%d/%m/%Y")
        context = {
            'reminder': reminder,
            'expiredDateTH': expiredDateTH
        }
        subject = reminder.subject
        from_email = 'SKT Reminder System <it.report@sanyo-kasei.co.th>'
        html_content = render_to_string('email/reminder.html', context)

        # เผื่อ fallback เป็น text
        text_content = "Reminder This is an alternative message in plain text."
        email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        email.attach_alternative(html_content, "text/html")
        email.send()
        
        return True
    except Exception as e:
        print(e)
        return False