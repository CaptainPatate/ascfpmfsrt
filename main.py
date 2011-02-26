import datetime
import logging
import os

from google.appengine.dist import use_library
use_library('django', '1.2')

from google.appengine.api import users
from google.appengine.ext import webapp, db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from models import Cfp, AuthorizedUser

# name, fullname, website, begin_conf_date, end_conf_date, submission_deadline,
# notification_date, country, city, acceptance_rate, submitters, category, keywords
# last_update

def authenticationRequired(user, handler):
    auth = AuthorizedUser.all()
    auth.filter('uid =', user.user_id())

    if not auth.get():
        logging.info('The unauthorized user "%s (%s) <%s>" tried to connect.',
                     user.nickname(), user.email(), user.user_id())
        handler.redirect('/out')

class OutHandler(webapp.RequestHandler):
    def get(self):
        html = os.path.join(os.path.dirname(__file__), 'templates/not_authorized.html')
        self.response.out.write(template.render(html, {'logout_url': users.create_logout_url("/")}))


class CfpView(webapp.RequestHandler):
    def get(self):
        authenticationRequired(users.get_current_user(), self)

        cfps = Cfp.all()
        cfps.filter('submission_deadline >=', datetime.date.today())
        cfps.order('submission_deadline')

        people = self.request.get('people')
        if people:
            cfps.filter('submitters IN', [users.User(people)])

        cfps = cfps.fetch(limit=200)

        html = os.path.join(os.path.dirname(__file__), 'templates/index.html')
        self.response.out.write(template.render(html, {'logout_url': users.create_logout_url("/"),
                                                       'nombre':len(cfps),'cfps':cfps}))


class AddCfpHandler(webapp.RequestHandler):
    def to_datetime(self, date):
        """convert string yyyy/mm/dd to a date object"""
        date = date.split('-')

        return datetime.date(int(date[0]),int(date[1]),int(date[2]))

    def get(self, nothing):
        authenticationRequired(users.get_current_user(), self)

        html = os.path.join(os.path.dirname(__file__), 'templates/add_cfp.html')
        self.response.out.write(template.render(html, {'logout_url': users.create_logout_url("/")}))

    def post(self, cfpid=None):
        authenticationRequired(users.get_current_user(), self)

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
        authenticationRequired(users.get_current_user(), self)

        if what == 'submit':
            user = users.get_current_user()
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
            cfps.order('submission_deadline').fetch(limit=200)
        elif what == 'submitters':
            authenticationRequired(users.get_current_user(), self)

            cfps = Cfp.all()
            cfps.filter('submission_deadline >=', datetime.date.today())
            cfps.order('submission_deadline').fetch(limit=200)
            # we can't make a query with two inequality conditions
            # so we filter in python in the pending of model redesign
            cfps = filter(lambda cfp: cfp.submitters != [], cfps)
        elif what == 'submitter':
            authenticationRequired(users.get_current_user(), self)

            cfps = Cfp.all()
            cfps.filter('submission_deadline >=', datetime.date.today())
            cfps.filter('submitters IN', [users.User(userid.replace('%40','@'))])
            cfps.order('submission_deadline').fetch(limit=200)
        else:
            self.response.set_status(404, 'Not Found')
            return      

        template_file = os.path.join(os.path.dirname(__file__), 'templates/cfp_atom.xml')
        self.response.headers['Content-Type'] = 'application/atom+xml; charset=utf-8'
        self.response.out.write(template.render(template_file, {'APPLICATION_ID':os.environ['APPLICATION_ID'],
                                                                'cfps':cfps}))


application = webapp.WSGIApplication([(r'/', CfpView),
                                      (r'/out', OutHandler),
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
