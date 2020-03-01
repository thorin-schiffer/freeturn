from snowpenguin.django.recaptcha2.fields import ReCaptchaField
from snowpenguin.django.recaptcha2.widgets import ReCaptchaWidget
from wagtail.contrib.forms.forms import FormBuilder
from wagtail.contrib.forms.models import AbstractEmailForm

CAPTCHA_FIELD_NAME = 'wagtailcaptcha'


class RecaptchaFormBuilder(FormBuilder):
    @property
    def formfields(self):
        fields = super().formfields
        fields[CAPTCHA_FIELD_NAME] = ReCaptchaField(widget=ReCaptchaWidget(), label='Captcha')
        return fields


class RecaptchaForm(AbstractEmailForm):
    form_builder = RecaptchaFormBuilder

    def process_form_submission(self, form):
        remove_captcha_field(form)
        return super().process_form_submission(form)

    class Meta:
        abstract = True


def remove_captcha_field(form):
    form.fields.pop(CAPTCHA_FIELD_NAME, None)
    form.cleaned_data.pop(CAPTCHA_FIELD_NAME, None)
