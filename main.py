#!/usr/bin/env python
import webapp2
import cgi
import jinja2
import os
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

class Blog(db.Model):
    title = db.StringProperty(required = True)
    blog_entry = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    read = db.BooleanProperty(required = True, default = False)

class Handler(webapp2.RequestHandler):
    """ A base RequestHandler class for our app.
        The other handlers inherit form this one.
    """

    def renderError(self, error_code):
        """ Sends an HTTP error code and a generic "oops!" message to the client. """

        self.error(error_code)
        self.response.write("Oops! Something went wrong.")

class MainHandler(Handler):
    def get(self):
        unread_blog = db.GqlQuery("SELECT * FROM Blog where read = False ORDER BY created ASC")
        t = jinja_env.get_template("front_page.html")
        content = t.render(
                        blog = unread_blog,
                        error = self.request.get("error"))
        self.response.write(content)

class RecentBlogs(Handler):
    def get(self):
        unread_blog = db.GqlQuery("SELECT * FROM Blog ORDER BY created ASC")
        t = jinja_env.get_template("front_page.html")
        content = t.render(
                        blog = unread_blog,
                        error = self.request.get("error"))
        self.response.write(content)

class AddEntry(Handler):
    def post(self):
        entry_title = self.request.get("title")
        entry_blog = self.request.get("new-entry")
        title = Blog(title = entry_title)
        blog = Blog(blog_entry = entry_blog)
        blog.put()

        t = jinja_env.get_template("entryadded.html")
        content = t.render()
        self.response.write(content)

class NewPost(Handler):
    def get(self):
        t = jinja_env.get_template("newpost.html")
        content = t.render()
        self.response.write(content)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/newpost', NewPost),
    ('/add', AddEntry),
    ('/blog', RecentBlogs)
], debug=True)
