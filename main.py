import datetime
import os

from google.appengine.api import users
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from models import Cfp

# name, fullname, website, begin_conf_date, end_conf_date, submission_deadline,
# notification_date, country, city, acceptance_rate, submitters, category, keywords
# last_update

class CfpView(webapp.RequestHandler):
    def get(self):

        cfps = Cfp.all()
        cfps.filter('submission_deadline >=', datetime.date.today())
        cfps.order('submission_deadline')

        people = self.request.get('people')
        if people:
            cfps.filter('submitters IN', [users.User(people)])

        cfps = cfps.fetch(limit=50)

        html = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(html, {'logout_url': users.create_logout_url("/"),
                                                       'nombre':len(cfps),'cfps':cfps}))


class AddCfpHandler(webapp.RequestHandler):
    def to_datetime(self, date):
        """convert string yyyy/mm/dd to a date object"""
        date = date.split('-')

        return datetime.date(int(date[0]),int(date[1]),int(date[2]))

    def get(self, nothing):
        html = os.path.join(os.path.dirname(__file__), 'templates/add_cfp.html')
        self.response.out.write(template.render(html, {'logout_url': users.create_logout_url("/")}))

    def post(self, cfpid=None):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))
        if not cfpid:
            cfp = Cfp()
        else:
            cfp = db.get(cfpid)

        cfp.name = self.request.get('name')
        cfp.fullname = self.request.get('fullname')
        cfp.setWebsite(self.request.get('website'))
        cfp.category = self.request.get('category')
        cfp.begin_conf_date = self.to_datetime(self.request.get('begin_conf_date'))
        cfp.end_conf_date = self.to_datetime(self.request.get('end_conf_date'))
        cfp.submission_deadline = self.to_datetime(self.request.get('submission_deadline'))
        cfp.notification_date = self.to_datetime(self.request.get('notification_date'))
        cfp.country = self.request.get('country')
        cfp.city = self.request.get('city')
        cfp.keywords = [self.request.get('keywords')]
        cfp.setAcceptanceRate(self.request.get('acceptance_rate'))

        cfp.put()
        self.redirect('/')


class UpdateHandler(webapp.RequestHandler):
    def get(self, what, cfpid):
        user = users.get_current_user()
        if not user:
            self.redirect(users.create_login_url(self.request.uri))

        if what == 'submit':
            cfp = db.get(cfpid)
            if user not in cfp.submitters:
                cfp.submitters.append(user)
                cfp.put()
            self.redirect('/')
        elif what == 'update':
            cfp = db.get(cfpid)
            html = os.path.join(os.path.dirname(__file__), 'templates/add_cfp.html')
            self.response.out.write(template.render(html, {'cfp':cfp}))
        else:
            self.response.set_status(404, 'Not Found')
            return


class FeedHandler(webapp.RequestHandler):
    def get(self, what, userid=None):
        if what == 'all':
            cfps = Cfp.all()
            cfps.filter('submission_deadline >=', datetime.date.today())
            cfps.order('submission_deadline').fetch(limit=50)
        elif what == 'submitters':
            user = users.get_current_user()
            if user:
                cfps = Cfp.all()
                cfps.filter('submission_deadline >=', datetime.date.today())
                cfps.order('submission_deadline').fetch(limit=50)
                # we can't make a query with two inequality conditions
                # so we filter in python in the pending of model redesign
                cfps = filter(lambda cfp: cfp.submitters != [], cfps)
            else:
                self.redirect(users.create_login_url(self.request.uri))
        elif what == 'submitter':
            user = users.get_current_user()
            if user:
                cfps = Cfp.all()
                cfps.filter('submission_deadline >=', datetime.date.today())
                cfps.filter('submitters IN', [users.User(userid.replace('%40','@'))])
                cfps.order('submission_deadline').fetch(limit=50)
            else:
                self.redirect(users.create_login_url(self.request.uri))
        else:
            self.response.set_status(404, 'Not Found')
            return      

        template_file = os.path.join(os.path.dirname(__file__), 'templates/cfp_atom.xml')
        self.response.headers['Content-Type'] = 'application/atom+xml; charset=utf-8'
        self.response.out.write(template.render(template_file, {'APPLICATION_ID':os.environ['APPLICATION_ID'],
                                                                'cfps':cfps}))


application = webapp.WSGIApplication([(r'/', CfpView),
                                      (r'/addcfp/(.*)', AddCfpHandler),
                                      (r'/(submit)/(.*)', UpdateHandler),
                                      (r'/(update)/(.*)', UpdateHandler),
                                      (r'/feed/(all)', FeedHandler),
                                      (r'/feed/(submitters)', FeedHandler),
                                      (r'/feed/(submitter)/(.*)', FeedHandler)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
