from app_safety_system.models.greenyellow_card import GreenYellowCard, GreenYellowType
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
    
def sendMailGreenYellowCard(gyCard: GreenYellowCard):
    try:
        if not gyCard:
            return False
        if not gyCard.emailIssueTo and gyCard.emailIssueTo == "Foreigner":
            return False
        
        # to_email = [str(settings.MAIL_CHAKU)]
        to_email = gyCard.emailIssueTo
        cc = ['safety_skt@sanyo-chemical.group']
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