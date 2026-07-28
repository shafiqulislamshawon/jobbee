from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

def send_html_email(subject, template_name, context, to_email):
    """
    Sends an HTML email using the specified template and context.
    """
    html_content = render_to_string(template_name, context)
    text_content = strip_tags(html_content)
    
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@jobbee.com',
        to=[to_email]
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()
