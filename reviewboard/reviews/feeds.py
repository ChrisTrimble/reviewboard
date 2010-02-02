from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.syndication.feeds import Feed
from django.core.exceptions import ObjectDoesNotExist
from django.utils.feedgenerator import Atom1Feed
from djblets.siteconfig.models import SiteConfiguration

from reviewboard.reviews.models import Group, ReviewRequest, Review


def add_domain(url):
    if not (url.startswith("http://") or url.startswith("https://")):
        siteconfig = SiteConfiguration.objects.get_current()

        url = "%s://%s%s" % (siteconfig.get("site_domain_method"),
                             Site.objects.get_current().domain,
                             url)

    return url

class BaseReviewFeed(Feed):
    """
    BaseReviewFeed: Base class for all the feeds generation
    feeds objects can either be review_request object or a review object
    """
    title_template = "feeds/reviews_title.html"
    description_template = "feeds/reviews_description.html"

    def item_author_link(self, item):
        return add_domain(self.get_review_request(item).submitter.get_absolute_url())

    def item_author_name(self, item):
        return self.get_review_request(item).submitter.username

    def item_author_email(self, item):
        return self.get_review_request(item).submitter.email

    def item_pubdate(self, item):
        return self.get_review_request(item).last_updated

    def item_link(self, obj):
        return add_domain(self.get_review_request(obj).get_absolute_url())
    
    def get_review_request(self, item):
        if isinstance(item, ReviewRequest) :
            return item
        else:
            return item.review_request


# RSS Feeds
class RssReviewsFeed(BaseReviewFeed):
    title = "Review Requests"
    link = "/r/all/"
    description = "All pending review requests."

    def items(self):
        return ReviewRequest.objects.public()[:20]


class RssSubmitterReviewsFeed(BaseReviewFeed):
    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist

        return User.objects.get(username=bits[0])

    def title(self, submitter):
        return u"Review requests to %s" % submitter

    def link(self, submitter):
        return add_domain(submitter.get_absolute_url())

    def description(self, submitter):
        return u"Pending review requests to %s" % submitter

    def items(self, submitter):
        """Creates a feeds_objs list, which contains review_request and 
        reviews object sorted on their last updated time
        """
        review_requests =  ReviewRequest.objects.to_user_directly(submitter.username).\
            order_by('-last_updated')[:20]
        feeds_objs = []
        for review_request in review_requests :
            if review_request.last_review_timestamp == None:
                feeds_objs.append(review_request)
            else :
                review_list =  Review.objects. \
                    get_published_reviews(review_request, submitter.username)
                for review in review_list :
                    feeds_objs.append(review)
        
        return feeds_objs

class RssGroupReviewsFeed(BaseReviewFeed):
    def get_object(self, bits):
        if len(bits) != 1:
            raise ObjectDoesNotExist

        return Group.objects.get(name=bits[0])

    def title(self, group):
        return u"Review requests to group %s" % group

    def link(self, group):
        return add_domain(group.get_absolute_url())

    def description(self, group):
        return u"Pending review requests to %s" % group

    def items(self, group):
        return ReviewRequest.objects.to_group(group).\
            order_by('-last_updated')[:20]
    
    def item_pubdate(self, item):
        """
        Takes an item, as returned by items(), and returns the item's pubdate.
        The publication date of the item will be its submission date
        """
        return item.last_review_timestamp

# Atom feeds
class AtomReviewsFeed(RssReviewsFeed):
    feed_type = Atom1Feed

class AtomSubmitterReviewsFeed(RssSubmitterReviewsFeed):
    feed_type = Atom1Feed

class AtomGroupReviewsFeed(RssGroupReviewsFeed):
    feed_type = Atom1Feed
