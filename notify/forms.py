from django import forms
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3

CHOICES = (
    ('bug','Bug Report from Serol'),
    ('help', 'Help Request from Serol'),
    ('other', 'Feedback from Serol')
)

class ContactForm(forms.Form):
    from_email = forms.EmailField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)
    subject = forms.ChoiceField(required=True, choices=CHOICES)
    captcha = ReCaptchaField(widget=ReCaptchaV3)
