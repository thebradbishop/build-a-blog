#!/usr/bin/env python
import webapp2
import cgi
import jinja2
import os
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

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
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created desc LIMIT 5")
        t = jinja_env.get_template("front_page.html")
        content = t.render(blogs=blogs)
        self.response.write(content)

class RecentBlogs(Handler):
    def get(self):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created desc LIMIT 5")
        t = jinja_env.get_template("front_page.html")
        content = t.render(blogs=blogs)
        self.response.write(content)

class AddEntry(Handler):
    def post(self):
        title = self.request.get("title")
        entry_blog = self.request.get("entry_blog")
        if title == "" or entry_blog == "":
            t = jinja_env.get_template("front_page.html")
            content = t.render(title=title, entry_blog=entry_blog)
            self.redirect("/newpost?title={0}&entry_blog={1}".format(title,entry_blog))

        if title and entry_blog:
            b = Blog(title=title, entry_blog=entry_blog)
            b.put()

        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created desc LIMIT 5")
        t = jinja_env.get_template("front_page.html")
        content = t.render(blogs=blogs)
        self.response.write(content)

class NewPost(Handler):
    def get(self):
        title = self.request.get("title")
        entry_blog = self.request.get("entry_blog")
        t = jinja_env.get_template("newpost.html")
        content = t.render(title=title, entry_blog=entry_blog)
        self.response.write(content)

class AllBlogs(Handler):
    def get(self):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created desc")
        t = jinja_env.get_template("front_page.html")
        content = t.render(blogs=blogs)
        self.response.write(content)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/newpost', NewPost),
    ('/add', AddEntry),
    ('/blog', RecentBlogs),
    ('/all', AllBlogs)
], debug=True)
