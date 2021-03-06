from google.appengine.ext import db
from google.appengine.api.users import User

class Cfp(db.Model):
    name = db.StringProperty()
    fullname = db.StringProperty()
    website = db.LinkProperty()
    begin_conf_date = db.DateProperty()
    end_conf_date = db.DateProperty()
    submission_deadline = db.DateProperty()
    notification_date = db.DateProperty()
    country = db.StringProperty()
    city = db.StringProperty()
    rate = db.RatingProperty()
    submitters = db.ListProperty(User)
    category = db.StringProperty()
    keywords = db.StringListProperty()
    last_update = db.DateTimeProperty(auto_now=True)

    def setWebsite(self, link):
        self.website = db.Link(link)

    def setAcceptanceRate(self, rate):
        if rate == '':
            self.rate = None
        else:
            self.rate = db.Rating(rate)

    def rfc3339_update(self):
        return self.last_update.strftime('%Y-%m-%dT%H:%M:%SZ')

    def submittersNickname(self):
        return map(lambda u: u.nickname(), self.submitters)

    def isSecurity(self):
        return 'Security' in self.keywords

    def isOS(self):
        return 'OS' in self.keywords

    def isSmartcard(self):
        return 'Smartcard' in self.keywords


class AuthorizedUser(db.Model):
    uid = db.StringProperty()
    nickname = db.StringProperty()
    email = db.StringProperty()
