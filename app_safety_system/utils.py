from bson import ObjectId
from app_safety_system.models.greenyellow_card import GreenYellowCard, GreenYellowType
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from app_safety_system.models.safety_setting import SafetySetting
    
def sendMailGreenYellowCard(gyCard: GreenYellowCard):
    try:
        if not gyCard:
            return False
        if not gyCard.emailIssueTo and gyCard.emailIssueTo == "Foreigner":
            return False
        
        # to_email = [str(settings.MAIL_CHAKU)]
        to_email = gyCard.emailIssueTo if len(gyCard.emailIssueTo) > 0 else ['safety_skt@sanyo-chemical.group']
        cc = ['safety_skt@sanyo-chemical.group'] if len(gyCard.emailIssueTo) > 0 else []
         # เตรียม context สำหรับ template
        gc = gyCard.serialize()
        context = {
            'gc': gc,
        }
        if gyCard.type.value == GreenYellowType.GreenCard.value:
            subject = 'Green Card'
            from_email = 'Green Card System <it.report@sanyo-kasei.co.th>'
            html_content = render_to_string('email/greencard.html', context)
            # เผื่อ fallback เป็น text
            text_content = "Green Card This is an alternative message in plain text."
        else:
            subject = 'Yellow Card'
            from_email = 'Yellow Card System <it.report@sanyo-kasei.co.th>'
            html_content = render_to_string('email/yellowcard.html', context)
            # เผื่อ fallback เป็น text
            text_content = "Yellow Card This is an alternative message in plain text."
        
        # สร้าง object email
        email = EmailMultiAlternatives(subject, text_content, from_email, to_email, cc= cc)
        # email = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        email.attach_alternative(html_content, "text/html")
        email.send()
        return True
    except Exception as e:
        print(e)
        return False
    
def HasSftPermission(id: str, menu: str = None, checkAdmin: bool = False):
    try:
        result = False
        safetySetting: SafetySetting = SafetySetting.objects.filter(user = ObjectId(id)).first()
        if safetySetting:
            if checkAdmin == True:
                if safetySetting.isAdmin == True and safetySetting.isActive == True:
                    result = True
            else:
                if safetySetting.isActive == True:
                    if menu:
                        result = any(m.name == menu for m in safetySetting.menus)
        return result
    except Exception as e:
        print(e)
        return False