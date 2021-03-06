import datetime
import logging
import os

import webapp2

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.template import loader

from google.appengine.api import users
from google.appengine.ext import db

from models import Cfp, AuthorizedUser

# name, fullname, website, begin_conf_date, end_conf_date, submission_deadline,
# notification_date, country, city, acceptance_rate, submitters, category, keywords
# last_update

"""
Wrapper method around Django templating engine to emulate
the now legacy webapp templating engine.
This will be used as transition.
"""
class template(object):
    @staticmethod
    def render(path, values):
        return loader.render_to_string(path, values)

def authenticationRequired(user, handler):
    auth = AuthorizedUser.all()
    auth.filter('uid =', user.user_id())
    userOK = auth.get()

    if not userOK:
        logging.info('The unauthorized user "%s (%s) <%s>" tried to connect.',
                     user.nickname(), user.email(), user.user_id())
        handler.redirect('/out')
    elif not userOK.nickname or not userOK.email:
        userOK.nickname = user.nickname()
        userOK.email = user.email()
        userOK.put()

class OutHandler(webapp2.RequestHandler):
    def get(self):
        html = os.path.join(os.path.dirname(__file__), 'templates/not_authorized.html')
        self.response.out.write(template.render(html, {'logout_url': users.create_logout_url("/")}))


class CfpView(webapp2.RequestHandler):
    def get(self, view=None):
        authenticationRequired(users.get_current_user(), self)

        cfps = Cfp.all()
        color = 'nothing'
        editable = True
        if view == 'notification':
            cfps.filter('notification_date >=', datetime.date.today() - datetime.timedelta(days=7))
            cfps.order('notification_date').fetch(limit=200)
            # we can't make a query with two inequality conditions
            # so we filter in python in the pending of model redesign
            cfps = filter(lambda cfp: cfp.submitters != [], cfps)
            color = 'notification'
        elif view == 'old':
            cfps.filter('submission_deadline <', datetime.date.today())
            cfps.order('submission_deadline')
            cfps = cfps.fetch(limit=800)
            editable = False
        else:
            cfps.filter('submission_deadline >=', datetime.date.today())
            cfps.order('submission_deadline')
            cfps = cfps.fetch(limit=200)
            color = 'deadline'

        html = os.path.join(os.path.dirname(__file__), 'templates/minimal.html')
        self.response.out.write(template.render(html, {'logout_url': users.create_logout_url("/"),
                                                       'nombre':len(cfps),'cfps':cfps,
                                                       'color':color, 'editable': editable}))

class DetailsHandler(webapp2.RequestHandler):
    def get(self, cfpid):
        authenticationRequired(users.get_current_user(), self)

        cfp = db.get(cfpid)

        html = os.path.join(os.path.dirname(__file__), 'templates/details.html')
        self.response.out.write(template.render(html, {'logout_url': users.create_logout_url("/"),
                                                       'cfp':cfp}))



class AddCfpHandler(webapp2.RequestHandler):
    def to_datetime(self, date):
        """convert string yyyy/mm/dd to a date object"""
        date = date.split('-')

        return datetime.date(int(date[0]),int(date[1]),int(date[2]))

    def get(self, nothing):
        authenticationRequired(users.get_current_user(), self)

        html = os.path.join(os.path.dirname(__file__), 'templates/add_cfp.html')
        self.response.out.write(template.render(html, {'logout_url': users.create_logout_url("/"),
                                                       'user': users.get_current_user()}))

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
        cfp.keywords = self.request.get_all('keywords')
        cfp.setAcceptanceRate(self.request.get('acceptance_rate'))
        submit = self.request.get('submitters')

        user = users.get_current_user()
        if submit:
            if user not in cfp.submitters:
                cfp.submitters.append(users.User(submit))
                logging.debug('user = %s added ', cfp.submitters[0].email())
        elif user in cfp.submitters:
            cfp.submitters.remove(users.get_current_user())
            logging.debug('user = %s removed ', users.get_current_user())

        cfp.put()
        self.redirect('/')


class UpdateHandler(webapp2.RequestHandler):
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
            self.response.out.write(template.render(html, {'cfp':cfp,
                                                           'user': users.get_current_user()}))
        else:
            self.response.set_status(404, 'Not Found')
            return


class FeedHandler(webapp2.RequestHandler):
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


app = webapp2.WSGIApplication([(r'/', CfpView),
                               (r'/details/(.+)', DetailsHandler),
                               (r'/out', OutHandler),
                               (r'/addcfp/(.*)', AddCfpHandler),
                               (r'/(submit)/(.*)', UpdateHandler),
                               (r'/(update)/(.*)', UpdateHandler),
                               (r'/view/(notification)', CfpView),
                               (r'/view/(old)', CfpView),
                               (r'/feed/(all)', FeedHandler),
                               (r'/feed/(submitters)', FeedHandler),
                               (r'/feed/(submitter)/(.*)', FeedHandler)],
                              debug=True)
