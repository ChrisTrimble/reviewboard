from datetime import *
from optparse import OptionParser, make_option

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import NoArgsCommand
from django.template.loader import render_to_string

from notifications.email import get_email_address_for_user
from notifications.email import SpiffyEmailMessage
from reviewboard.reviews.models import ReviewRequest, Review


class Command(NoArgsCommand):
    help = 'Sent an e-mail reminder to submit a pending review request'

    option_list = NoArgsCommand.option_list + (
        make_option('--from_email', '-f', dest='from_email',
            help='Specify a from e-mail'),
    )

    parser = OptionParser(option_list=option_list)
    (options, args) = parser.parse_args()

    def handle(self, **options):
        """
        Sends an reminder e-mail to the review request submitter, if
        recieves a ship-it and still not submitted
        """
        current_site = Site.objects.get_current()
        siteconfig = current_site.config.get()
        queryset = ReviewRequest.objects.public()

        if not siteconfig.get('reminder_notification'):
            print "Reminder notification couldn't be sent"
            print "Administrator has disabled reminder notification"
            return

        for review_request in queryset:
            submitter = review_request.submitter
            submitter_profile = submitter.get_profile()
            reminder_notification_delay = submitter_profile. \
                                            reminder_notification_delay

            # User has disabled reminder notification
            if not submitter_profile.reminder_notification:
                continue
            public_reviews = review_request.get_public_reviews()
            reviews_without_shipit = filter(lambda a: \
                                            a.ship_it == 0, public_reviews)

            if (len(public_reviews) == 0 or len(reviews_without_shipit) > 0):
                # Either Review Request has not reviewed or reviews exists
                # which are not marked for ship-it
                continue
            else:
                timestamp_list = map(lambda a: a.timestamp, public_reviews)
                time_delta = datetime.now() - max(timestamp_list)

                if (time_delta.days >= submitter_profile. \
                                        reminder_notification_delay):
                    self.send_reminder_mail(review_request, time_delta.days,
                                     'notifications/submission_reminder.txt',
                                     'notifications/submission_reminder.html',
                                     siteconfig)

    def send_reminder_mail(self, review_request, pending_days,
                           text_template_name, html_template_name, siteconfig):

        subject = "[Submission Reminder]: " + review_request.summary

        from_email = self.options.from_email

        recipients = set([from_email])
        to_field = recipients

        if review_request.submitter.is_active:
            submitter = review_request.submitter
            recipients.add(get_email_address_for_user(submitter))

        domain_method = siteconfig.get("site_domain_method")

        context = {}
        context['pending_days'] = pending_days
        context['domain'] = current_site.domain
        context['domain_method'] = domain_method
        context['review_request'] = review_request

        text_body = render_to_string(text_template_name, context)
        html_body = render_to_string(html_template_name, context)

        message = SpiffyEmailMessage(subject.strip(), text_body, html_body,
                                     from_email, list(to_field), [], None)

        message.send()

        return message.message_id
