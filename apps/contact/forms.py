from django import forms
from django.utils.translation import gettext_lazy as _
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    # Honeypot field for spam bots
    website_hp = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContactMessage
        fields = ['full_name', 'phone', 'email', 'subject', 'message']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('أدخل اسمك الكريم')}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('مثال: 777000000')}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('name@example.com (اختياري)')}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('موضوع الاستفسار')}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': _('اكتب تفاصيل استفسارك هنا...')}),
        }

    def clean(self):
        cleaned_data = super().clean()
        hp = cleaned_data.get('website_hp')
        if hp:
            raise forms.ValidationError(_('تم رفض الطلب كإجراء أمني لمكافحة الرسائل المزعجة.'))
        return cleaned_data

