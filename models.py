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
    subitters = db.ListProperty(User)
    category = db.StringListProperty()
    keywords = db.StringListProperty()

    def setWebsite(self, link):
        self.website = db.Link(link)

    def setAcceptanceRate(self, rate):
        self.rate = db.Rating(rate)
