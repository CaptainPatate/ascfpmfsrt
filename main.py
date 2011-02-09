import datetime
import os

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from models import Cfp

# name, fullname, website, begin_conf_date, end_conf_date, submission_deadline,
# notification_date, country, city, acceptance_rate, subitters, category, keywords

class CfpView(webapp.RequestHandler):
    def get(self):
        cfps = Cfp.all().fetch(limit=5)

        html = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(html, {'logout_url': users.create_logout_url("/"), 
                                                       'nombre':len(cfps),'cfps':cfps}))


class AddCfpHandler(webapp.RequestHandler):
    def to_datetime(self, date):
        """convert string jj/mm/yyyy to a date object"""
        date = date.split('/')
        
        return datetime.date(int(date[2]),int(date[1]),int(date[0]))

    def get(self):
        html = os.path.join(os.path.dirname(__file__), 'add_cfp.html')
        self.response.out.write(template.render(html, {}))

    def post(self):
        user = users.get_current_user()
        if user:
            cfp = Cfp()
            cfp.name=self.request.get('name')
            cfp.fullname=self.request.get('fullname')
            cfp.setWebsite(self.request.get('link'))
            cfp.begin_conf_date=self.to_datetime(self.request.get('conf_date'))
            cfp.submission_deadline=self.to_datetime(self.request.get('submission_deadline'))
            cfp.notification_date=self.to_datetime(self.request.get('notification_date'))
            cfp.country=self.request.get('country')
            cfp.city=self.request.get('city')
            
            cfp.put()
            self.redirect('/')
        else:
            self.redirect(users.create_login_url(self.request.uri))


class FeedHandler(webapp.RequestHandler):
    """Handles the list of quotes ordered in reverse chronological order."""

    def get(self, what):
        """Retrieve a feed"""
        if what == 'all':    
            cfps = Cfp.gql('ORDER BY deadline_date').fetch(10)
        else:
            self.response.set_status(404, 'Not Found')
            return      

        template_file = os.path.join(os.path.dirname(__file__), 'templates/atom_feed.xml')    
        self.response.headers['Content-Type'] = 'application/atom+xml; charset=utf-8'
        self.response.out.write(template.render(template_file, template_values))


application = webapp.WSGIApplication([('/', CfpView),
                                      ('/addcfp', AddCfpHandler),
                                      ('/feed/(all)', FeedHandler)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
