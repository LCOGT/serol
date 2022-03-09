from django import forms

CHOICES = (
    ('bug','Bug Report from Serol'),
    ('help', 'Help Request from Serol'),
    ('other', 'Feedback from Serol')
)

class ContactForm(forms.Form):
    from_email = forms.EmailField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)
    subject = forms.ChoiceField(required=True, choices=CHOICES)
