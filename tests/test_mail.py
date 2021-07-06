from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.test import SimpleTestCase as TestCase

from sgbackend import SendGridBackend

settings.configure()


class SendGridBackendTests(TestCase):
    def test_raises_if_sendgrid_api_key_doesnt_exists(self):
        with self.assertRaises(ImproperlyConfigured):
            SendGridBackend()

    def test_if_not_emails(self):
        with self.settings(SENDGRID_API_KEY='test_key'):
            SendGridBackend().send_messages(emails=[])

    def test_build_empty_sg_mail(self):
        msg = EmailMessage()
        with self.settings(SENDGRID_API_KEY='test_key'):
            mail = SendGridBackend()._build_sg_mail(msg)
            self.assertEqual(
                mail,
                {'from': {'email': 'webmaster@localhost'},
                 'subject': '',
                 'mail_settings': {},
                 'content': [{'type': 'text/plain', 'value': ''}],
                 'personalizations': [{'subject': ''}]}
            )

    def test_build_w_to_sg_email(self):
        msg = EmailMessage(to=('andrii.soldatenko@test.com',))
        with self.settings(SENDGRID_API_KEY='test_key'):
            mail = SendGridBackend()._build_sg_mail(msg)
            self.assertEqual(
                mail,
                {'content': [{'value': '', 'type': 'text/plain'}],
                 'personalizations': [
                     {'to': [{'email': 'andrii.soldatenko@test.com'}],
                      'subject': ''}],
                  'mail_settings': {},
                 'from': {'email': 'webmaster@localhost'}, 'subject': ''}
            )

    def test_build_w_cc_sg_email(self):
        msg = EmailMessage(cc=('andrii.soldatenko@test.com',))
        with self.settings(SENDGRID_API_KEY='test_key'):
            mail = SendGridBackend()._build_sg_mail(msg)
            self.assertEqual(
                mail,
                {'content': [{'value': '', 'type': 'text/plain'}],
                 'personalizations': [
                     {'cc': [{'email': 'andrii.soldatenko@test.com'}],
                      'subject': ''}],
                      'mail_settings': {},
                 'from': {'email': 'webmaster@localhost'}, 'subject': ''}
            )

    def test_build_w_bcc_sg_email(self):
        msg = EmailMessage(bcc=('andrii.soldatenko@test.com',))
        with self.settings(SENDGRID_API_KEY='test_key'):
            mail = SendGridBackend()._build_sg_mail(msg)
            self.assertEqual(
                mail,
                {'content': [{'value': '', 'type': 'text/plain'}],
                 'personalizations': [
                     {'bcc': [{'email': 'andrii.soldatenko@test.com'}],
                      'subject': ''}],
                      'mail_settings': {},
                 'from': {'email': 'webmaster@localhost'}, 'subject': ''}
            )

    def test_build_w_reply_to_sg_email(self):
        # Test setting a Reply-To header.
        msg = EmailMessage()
        msg.extra_headers = {'Reply-To': 'andrii.soldatenko@test.com'}
        with self.settings(SENDGRID_API_KEY='test_key'):
            mail = SendGridBackend()._build_sg_mail(msg)
            self.assertEqual(
                mail,
                {'content': [{'value': '', 'type': 'text/plain'}],
                 'personalizations': [{'subject': ''}],
                 'mail_settings': {},
                 'reply_to': {'email': 'andrii.soldatenko@test.com'},
                 'from': {'email': 'webmaster@localhost'}, 'subject': ''}
            )
        # Test using the reply_to attribute.
        msg = EmailMessage(reply_to=('andrii.soldatenko@test.com',))
        with self.settings(SENDGRID_API_KEY='test_key'):
            mail = SendGridBackend()._build_sg_mail(msg)
            self.assertEqual(
                mail,
                {'content': [{'value': '', 'type': 'text/plain'}],
                 'personalizations': [{'subject': ''}],
                 'mail_settings': {},
                 'reply_to': {'email': 'andrii.soldatenko@test.com'},
                 'from': {'email': 'webmaster@localhost'}, 'subject': ''}
            )
        # Test using "name <email>" format.
        msg = EmailMessage(
            reply_to=('Andrii Soldatenko <andrii.soldatenko@test.com>',))
        with self.settings(SENDGRID_API_KEY='test_key'):
            mail = SendGridBackend()._build_sg_mail(msg)
            self.assertEqual(
                mail,
                {'content': [{'value': '', 'type': 'text/plain'}],
                 'personalizations': [{'subject': ''}],
                 'mail_settings': {},
                 'reply_to': {
                    'name': 'Andrii Soldatenko',
                    'email': 'andrii.soldatenko@test.com'},
                 'from': {'email': 'webmaster@localhost'}, 'subject': ''}
            )

    def test_build_empty_multi_alternatives_sg_email(self):
        html_content = '<p>This is an <strong>important</strong> message.</p>'
        msg = EmailMultiAlternatives()
        msg.attach_alternative(html_content, "text/html")
        with self.settings(SENDGRID_API_KEY='test_key'):
            mail = SendGridBackend()._build_sg_mail(msg)
            self.assertEqual(
                mail,
                {'content': [{'type': 'text/plain', 'value': ''},
                             {'type': 'text/html',
                              'value': '<p>This is an '
                                       '<strong>important</strong> '
                                       'message.</p>'}],
                 'from': {'email': 'webmaster@localhost'},
                 'personalizations': [{'subject': ''}],
                 'mail_settings': {},
                 'subject': ''}
            )

    def test_build_sg_email_w_categories(self):
        msg = EmailMessage()
        msg.categories = ['name']
        with self.settings(SENDGRID_API_KEY='test_key'):
            mail = SendGridBackend()._build_sg_mail(msg)
            self.assertEqual(
                mail,
                {'categories': ['name'],
                 'content': [{'type': 'text/plain', 'value': ''}],
                 'from': {'email': 'webmaster@localhost'},
                 'personalizations': [{'subject': ''}],
                 'mail_settings': {},
                 'subject': ''
                 }
            )

    def test_build_sg_email_w_template_id(self):
        msg = EmailMessage()
        msg.template_id = 'template_id_123456'
        with self.settings(SENDGRID_API_KEY='test_key'):
            mail = SendGridBackend()._build_sg_mail(msg)
            self.assertEqual(
                mail,
                {'template_id': 'template_id_123456',
                 'content': [{'type': 'text/plain', 'value': ''}],
                 'from': {'email': 'webmaster@localhost'},
                 'personalizations': [{'subject': ''}],
                 'subject': '',
                 'mail_settings': {},
                 }
            )

    def test_build_sg_email_w_substitutions(self):
        msg = EmailMessage()
        msg.substitutions = {}
        with self.settings(SENDGRID_API_KEY='test_key'):
            mail = SendGridBackend()._build_sg_mail(msg)
            self.assertEqual(
                mail,
                {'content': [{'type': 'text/plain', 'value': ''}],
                 'from': {'email': 'webmaster@localhost'},
                 'personalizations': [{'subject': ''}],
                 'mail_settings': {},
                 'subject': ''}
            )

    def test_build_sg_email_w_extra_headers(self):
        msg = EmailMessage()
        msg.extra_headers = {'EXTRA_HEADER': 'VALUE'}
        with self.settings(SENDGRID_API_KEY='test_key'):
            mail = SendGridBackend()._build_sg_mail(msg)
            self.assertEqual(
                mail,
                {'content': [{'type': 'text/plain', 'value': ''}],
                 'from': {'email': 'webmaster@localhost'},
                 'headers': {'EXTRA_HEADER': 'VALUE'},
                 'personalizations': [{'subject': ''}],
                 'mail_settings': {},
                 'subject': ''}
            )

    def test_build_sg_email_w_custom_args(self):
        msg = EmailMessage()
        msg.custom_args = {'custom_arg1': '12345-abcdef'}
        with self.settings(SENDGRID_API_KEY='test_key'):
            mail = SendGridBackend()._build_sg_mail(msg)
            self.assertEqual(
                mail,
                {'content': [{'type': 'text/plain', 'value': ''}],
                 'custom_args': {'custom_arg1': '12345-abcdef'},
                 'from': {'email': 'webmaster@localhost'},
                 'personalizations': [{'subject': ''}],
                 'mail_settings': {},
                 'subject': ''}
            )

    def test_list_management_bypass_true(self):
        msg = EmailMessage()
        msg.bypass_list_management = True
        with self.settings(SENDGRID_API_KEY='test_key'):
            mail = SendGridBackend()._build_sg_mail(msg)
            self.assertEqual(
                mail,
                {'content': [{'type': 'text/plain', 'value': ''}],
                 'from': {'email': 'webmaster@localhost'},
                 'personalizations': [{'subject': ''}],
                 'mail_settings': {
                     'bypass_list_management': {
                         'enable': True
                     }
                 },
                 'subject': ''}
            )

    def test_list_management_bypass_false(self):
        msg = EmailMessage()
        msg.bypass_list_management = False
        with self.settings(SENDGRID_API_KEY='test_key'):
            mail = SendGridBackend()._build_sg_mail(msg)
            self.assertEqual(
                mail,
                {'content': [{'type': 'text/plain', 'value': ''}],
                 'from': {'email': 'webmaster@localhost'},
                 'personalizations': [{'subject': ''}],
                 'mail_settings': {
                     'bypass_list_management': {
                         'enable': False
                     }
                 },
                 'subject': ''}
            )

    def test_sandbox_true_no_whitelists_no_to(self):
        msg = EmailMessage(to=[])
        with self.settings(
            SENDGRID_API_KEY='test_key',
            SENDGRID_SANDBOX=True
        ):
            mail = SendGridBackend()._build_sg_mail(msg)
            self.assertEqual(
                mail,
                {'content': [{'type': 'text/plain', 'value': ''}],
                 'from': {'email': 'webmaster@localhost'},
                 'personalizations': [{'subject': ''}],
                 'mail_settings': {
                     'sandbox_mode': {
                         'enable': True
                     }
                 },
                 'subject': ''}
            )
    
    def test_sandbox_true_no_whitelists(self):
        msg = EmailMessage(to=['test@example.com'])
        with self.settings(
            SENDGRID_API_KEY='test_key',
            SENDGRID_SANDBOX=True
        ):
            mail = SendGridBackend()._build_sg_mail(msg)
            self.assertEqual(
                mail,
                {'content': [{'type': 'text/plain', 'value': ''}],
                 'from': {'email': 'webmaster@localhost'},
                 'personalizations': [{'subject': '', 'to': [
                     {'email': 'test@example.com'}
                 ]}],
                 'mail_settings': {
                     'sandbox_mode': {
                         'enable': True
                     }
                 },
                 'subject': ''}
            )

    def test_sandbox_true_no_whitelists_multiple_to(self):
        msg = EmailMessage(to=['test@example.com', 'test@example.org'])
        with self.settings(
            SENDGRID_API_KEY='test_key',
            SENDGRID_SANDBOX=True
        ):
            mail = SendGridBackend()._build_sg_mail(msg)
            self.assertEqual(
                mail,
                {'content': [{'type': 'text/plain', 'value': ''}],
                 'from': {'email': 'webmaster@localhost'},
                 'personalizations': [{'subject': '', 'to': [
                     {'email': 'test@example.com'},
                     {'email': 'test@example.org'}
                 ]}],
                 'mail_settings': {
                     'sandbox_mode': {
                         'enable': True
                     }
                 },
                 'subject': ''}
            )

    def test_sandbox_true_w_domain_whitelist_match_none(self):
        msg = EmailMessage(to=['test@example.com','test@example.net'])
        with self.settings(
            SENDGRID_API_KEY='test_key',
            SENDGRID_SANDBOX=True,
            SENDGRID_SANDBOX_WHITELIST_DOMAINS=['foo.com']
        ):
            mail = SendGridBackend()._build_sg_mail(msg)
            self.assertEqual(
                mail,
                {'content': [{'type': 'text/plain', 'value': ''}],
                 'from': {'email': 'webmaster@localhost'},
                 'personalizations': [{'subject': '', 'to': [
                     {'email': 'test@example.com'},
                     {'email': 'test@example.net'}
                 ]}],
                 'mail_settings': {
                     'sandbox_mode': {
                         'enable': True
                     }
                 },
                 'subject': ''}
            )

    def test_sandbox_true_w_domain_whitelist_match_single(self):
        msg = EmailMessage(to=[
            'test@example.com',
            'test@example.net',
        ])
        with self.settings(
            SENDGRID_API_KEY='test_key',
            SENDGRID_SANDBOX=True,
            SENDGRID_SANDBOX_WHITELIST_DOMAINS=['example.com']
        ):
            mail = SendGridBackend()._build_sg_mail(msg)
            self.assertEqual(
                mail,
                {'content': [{'type': 'text/plain', 'value': ''}],
                 'from': {'email': 'webmaster@localhost'},
                 'personalizations': [{'subject': '', 'to': [
                     {'email': 'test@example.com'},
                     {'email': 'test@example.net'}
                 ]}],
                 'mail_settings': {},
                 'subject': ''}
            )

    def test_sandbox_true_w_domain_whitelist_match_all(self):
        msg = EmailMessage(to=['test@example.com', 'test@example.org'])
        with self.settings(
            SENDGRID_API_KEY='test_key',
            SENDGRID_SANDBOX=True,
            SENDGRID_SANDBOX_WHITELIST_DOMAINS=['example.com', 'example.org']
        ):
            mail = SendGridBackend()._build_sg_mail(msg)
            self.assertEqual(
                mail,
                {'content': [{'type': 'text/plain', 'value': ''}],
                 'from': {'email': 'webmaster@localhost'},
                 'personalizations': [{'subject': '', 'to': [
                     {'email': 'test@example.com'},
                     {'email': 'test@example.org'}
                 ]}],
                 'mail_settings': {},
                 'subject': ''}
            )

    def test_sandbox_true_w_regex_whitelist_address(self):
        msg = EmailMessage(to=['test@example.com'])
        msg_2 = EmailMessage(to=['test-test@example.com'])
        with self.settings(
            SENDGRID_API_KEY='test_key',
            SENDGRID_SANDBOX=True,
            SENDGRID_SANDBOX_WHITELIST_REGEX=['^test@example.com$']
        ):
            mail = SendGridBackend()._build_sg_mail(msg)
            self.assertEqual(
                mail,
                {'content': [{'type': 'text/plain', 'value': ''}],
                 'from': {'email': 'webmaster@localhost'},
                 'personalizations': [{'subject': '', 'to': [
                     {'email': 'test@example.com'}
                 ]}],
                 'mail_settings': {},
                 'subject': ''}
            )
            mail = SendGridBackend()._build_sg_mail(msg_2)
            self.assertEqual(
                mail,
                {'content': [{'type': 'text/plain', 'value': ''}],
                 'from': {'email': 'webmaster@localhost'},
                 'personalizations': [{'subject': '', 'to': [
                     {'email': 'test-test@example.com'}
                 ]}],
                 'mail_settings': {
                     'sandbox_mode': {
                         'enable': True
                     }
                 },
                 'subject': ''}
            )

    def test_sandbox_true_w_regex_whitelist_domain(self):
        msg = EmailMessage(to=['test@example.com'])
        msg_2 = EmailMessage(to=['test@example.com.au'])
        with self.settings(
            SENDGRID_API_KEY='test_key',
            SENDGRID_SANDBOX=True,
            SENDGRID_SANDBOX_WHITELIST_REGEX=['.*@example.com$']
        ):
            mail = SendGridBackend()._build_sg_mail(msg)
            self.assertEqual(
                mail,
                {'content': [{'type': 'text/plain', 'value': ''}],
                 'from': {'email': 'webmaster@localhost'},
                 'personalizations': [{'subject': '', 'to': [
                     {'email': 'test@example.com'}
                 ]}],
                 'mail_settings': {},
                 'subject': ''}
            )
            mail = SendGridBackend()._build_sg_mail(msg_2)
            self.assertEqual(
                mail,
                {'content': [{'type': 'text/plain', 'value': ''}],
                 'from': {'email': 'webmaster@localhost'},
                 'personalizations': [{'subject': '', 'to': [
                     {'email': 'test@example.com.au'}
                 ]}],
                 'mail_settings': {
                     'sandbox_mode': {
                         'enable': True
                     }
                 },
                 'subject': ''}
            )

    def test_sandbox_true_w_regex_whitelist_username(self):
        msg = EmailMessage(to=['test@example.com'])
        msg_2 = EmailMessage(to=['test-test@example.com'])
        with self.settings(
            SENDGRID_API_KEY='test_key',
            SENDGRID_SANDBOX=True,
            SENDGRID_SANDBOX_WHITELIST_REGEX=['^test@.*$']
        ):
            mail = SendGridBackend()._build_sg_mail(msg)
            self.assertEqual(
                mail,
                {'content': [{'type': 'text/plain', 'value': ''}],
                 'from': {'email': 'webmaster@localhost'},
                 'personalizations': [{'subject': '', 'to': [
                     {'email': 'test@example.com'}
                 ]}],
                 'mail_settings': {},
                 'subject': ''}
            )
            mail = SendGridBackend()._build_sg_mail(msg_2)
            self.assertEqual(
                mail,
                {'content': [{'type': 'text/plain', 'value': ''}],
                 'from': {'email': 'webmaster@localhost'},
                 'personalizations': [{'subject': '', 'to': [
                     {'email': 'test-test@example.com'}
                 ]}],
                 'mail_settings': {
                     'sandbox_mode': {
                         'enable': True
                     }
                 },
                 'subject': ''}
            )

    def test_sandbox_true_w_domain_and_regex_whitelist(self):
        msg = EmailMessage(to=['test@example.com'])
        msg_2 = EmailMessage(to=['test@example.net'])
        msg_3 = EmailMessage(to=['test@example.org'])
        with self.settings(
            SENDGRID_API_KEY='test_key',
            SENDGRID_SANDBOX=True,
            SENDGRID_SANDBOX_WHITELIST_DOMAINS=['example.com'],
            SENDGRID_SANDBOX_WHITELIST_REGEX=['^test@example.net$']
        ):
            mail = SendGridBackend()._build_sg_mail(msg)
            self.assertEqual(
                mail,
                {'content': [{'type': 'text/plain', 'value': ''}],
                 'from': {'email': 'webmaster@localhost'},
                 'personalizations': [{'subject': '', 'to': [
                     {'email': 'test@example.com'}
                 ]}],
                 'mail_settings': {},
                 'subject': ''}
            )
            mail = SendGridBackend()._build_sg_mail(msg_2)
            self.assertEqual(
                mail,
                {'content': [{'type': 'text/plain', 'value': ''}],
                 'from': {'email': 'webmaster@localhost'},
                 'personalizations': [{'subject': '', 'to': [
                     {'email': 'test@example.net'}
                 ]}],
                 'mail_settings': {},
                 'subject': ''}
            )
            mail = SendGridBackend()._build_sg_mail(msg_3)
            self.assertEqual(
                mail,
                {'content': [{'type': 'text/plain', 'value': ''}],
                 'from': {'email': 'webmaster@localhost'},
                 'personalizations': [{'subject': '', 'to': [
                     {'email': 'test@example.org'}
                 ]}],
                 'mail_settings': {
                     'sandbox_mode': {
                         'enable': True
                     }
                 },
                 'subject': ''}
            )
