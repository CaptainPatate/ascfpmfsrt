import datetime
import os

from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

class Cfp(db.Model):
    name = db.StringProperty()
    fullname = db.StringProperty()
    link = db.Link("hhtp://www.google.com")
    conf_date = db.DateProperty()
    submission_deadline = db.DateProperty()
    notification_date = db.DateProperty()
    country = db.StringProperty()
    city = db.StringProperty()

class MainPage(webapp.RequestHandler):
    def get(self):
        cfps = Cfp.all().fetch(limit=5)

        html = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(html, {'nombre':len(cfps),'cfps':cfps}))

class AddCfpHandler(webapp.RequestHandler):
    def to_datetime(self, date):
        """convert string jj/mm/yyyy to a date object"""
        date = date.split('/')
        
        return datetime.date(int(date[2]),int(date[1]),int(date[0]))

    def get(self):
        html = os.path.join(os.path.dirname(__file__), 'add_cfp.html')
        self.response.out.write(template.render(html, {}))

    def post(self):
        cfp = Cfp(name=self.request.get('name'),
                  full_name=self.request.get('fullname'),
                  link=self.request.get('link'),
                  conf_date=self.to_datetime(self.request.get('conf_date')),
                  submission_deadline=self.to_datetime(self.request.get('submission_deadline')),
                  notification_date=self.to_datetime(self.request.get('notification_date')),
                  country=self.request.get('country'),
                  city=self.request.get('city'))
        cfp.put()
        self.redirect('/')

application = webapp.WSGIApplication([('/', MainPage),
                                      ('/addcfp', AddCfpHandler)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
