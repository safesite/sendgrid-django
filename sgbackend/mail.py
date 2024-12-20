from sgbackend.sandbox_settings import can_enable_sandbox_mode
from .version import __version__

import base64
import sys
from email.mime.base import MIMEBase
from python_http_client.exceptions import HTTPError

try:
    import rfc822
except ImportError:
    import email.utils as rfc822

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.base import BaseEmailBackend

import sendgrid
from sendgrid.helpers.mail import (
    Attachment,
    Category,
    Content,
    CustomArg,
    Email,
    Mail,
    Personalization,
    Substitution,
    MailSettings,
    SandBoxMode,
    BypassListManagement
)


class SendGridBackend(BaseEmailBackend):
    '''
    SendGrid Web API Backend
    '''
    def __init__(self, fail_silently=False, **kwargs):
        super(SendGridBackend, self).__init__(
            fail_silently=fail_silently, **kwargs)
        if 'api_key' in kwargs:
            self.api_key = kwargs['api_key']
        else:
            self.api_key = getattr(settings, "SENDGRID_API_KEY", None)

        if not self.api_key:
            raise ImproperlyConfigured('''
                SENDGRID_API_KEY must be declared in settings.py''')

        self.sg = sendgrid.SendGridAPIClient(apikey=self.api_key)
        self.version = 'sendgrid/{0};django'.format(__version__)
        self.sg.client.request_headers['User-agent'] = self.version

    def send_messages(self, emails):
        '''
        Comments
        '''
        if not emails:
            return

        count = 0
        for email in emails:
            mail = self._build_sg_mail(email)
            try:
                self.sg.client.mail.send.post(request_body=mail)
                count += 1
            except HTTPError as e:
                if not self.fail_silently:
                    raise
        return count

    def _build_sg_mail(self, email):
        mail = Mail()
        from_name, from_email = rfc822.parseaddr(email.from_email)
        # Python sendgrid client should improve
        # sendgrid/helpers/mail/mail.py:164
        if not from_name:
            from_name = None
        mail.from_email = Email(from_email, from_name)
        mail.subject = email.subject

        mail_settings = MailSettings()

        personalization = Personalization()
        for e in email.to:
            personalization.add_to(Email(e))
        for e in email.cc:
            personalization.add_cc(Email(e))
        for e in email.bcc:
            personalization.add_bcc(Email(e))
        personalization.subject = email.subject
        if email.content_subtype == "html":
            mail.add_content(Content("text/html", email.body))
        else:
            mail.add_content(Content("text/plain", email.body))
        if isinstance(email, EmailMultiAlternatives):
            for alt in email.alternatives:
                if alt[1] == "text/html":
                    mail.add_content(Content(alt[1], alt[0]))
        elif email.content_subtype == "html":
            mail.contents = []
            mail.add_content(Content("text/plain", ' '))

        if hasattr(email, 'categories'):
            for c in email.categories:
                mail.add_category(Category(c))

        if hasattr(email, 'custom_args'):
            for k, v in email.custom_args.items():
                mail.add_custom_arg(CustomArg(k, v))

        # Used to override the list management (password reset etc)
        if hasattr(email, 'bypass_list_management'):
            mail_settings.bypass_list_management = BypassListManagement(email.bypass_list_management)
            
        #Check for sandbox mode
        if can_enable_sandbox_mode(email.to):
            mail_settings.sandbox_mode = SandBoxMode(True)

        if hasattr(email, 'template_id'):
            mail.template_id = email.template_id
            # Version 3 dynamic data  handle bars {{name}}
            if hasattr(email, 'dynamic_data'):
                personalization.dynamic_template_data = email.dynamic_data
            # Version 3 substitutions
            if hasattr(email, 'substitutions'):
                for key, value in email.substitutions.items():
                    personalization.add_substitution(Substitution(key, value))

        # SendGrid does not support adding Reply-To as an extra
        # header, so it needs to be manually removed if it exists.
        reply_to_string = ""
        for key, value in email.extra_headers.items():
            if key.lower() == "reply-to":
                reply_to_string = value
            else:
                mail.add_header({key: value})
        # Note that if you set a "Reply-To" header *and* the reply_to
        # attribute, the header's value will be used.
        if not mail.reply_to and hasattr(email, "reply_to") and email.reply_to:
            # SendGrid only supports setting Reply-To to a single address.
            # See https://github.com/sendgrid/sendgrid-csharp/issues/339.
            reply_to_string = email.reply_to[0]
        # Determine whether reply_to contains a name and email address, or
        # just an email address.
        if reply_to_string:
            reply_to_name, reply_to_email = rfc822.parseaddr(reply_to_string)
            if reply_to_name and reply_to_email:
                mail.reply_to = Email(reply_to_email, reply_to_name)
            elif reply_to_email:
                mail.reply_to = Email(reply_to_email)

        for attachment in email.attachments:
            if isinstance(attachment, MIMEBase):
                attach = Attachment()
                attach.filename = attachment.get_filename()
                attach.content = base64.b64encode(attachment.get_payload())
                mail.add_attachment(attach)
            elif isinstance(attachment, tuple):
                attach = Attachment()
                attach.filename = attachment[0]
                base64_attachment = base64.b64encode(attachment[1])
                if sys.version_info >= (3,):
                    attach.content = str(base64_attachment, 'utf-8')
                else:
                    attach.content = base64_attachment
                attach.type = attachment[2]
                mail.add_attachment(attach)

        mail.add_personalization(personalization)
        mail.mail_settings = mail_settings
        return mail.get()
