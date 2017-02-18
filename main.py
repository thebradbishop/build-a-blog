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
    entry_blog = db.StringProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

#def blog_id(self):
#    blog = db.GqlQuery("SELECT __key__ FROM Blog WHERE created = '2017-02-18 02:26:49'")
#    return blog

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
        content = t.render(
                    blogs=blogs,
                    )
        self.response.write(content)

class RecentBlogs(Handler):
    def get(self):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created desc LIMIT 5")
        t = jinja_env.get_template("front_page.html")
        content = t.render(
                    blogs=blogs
                    )
        self.response.write(content)

class NewPost(Handler):
    def get(self):
        title = self.request.get("title")
        entry_blog = self.request.get("entry_blog")
        error_title = self.request.get("error_title")
        error_entry = self.request.get("error_entry")
        t = jinja_env.get_template("newpost.html")
        content = t.render(title=title, entry_blog=entry_blog, error_title=error_title, error_entry=error_entry)
        self.response.write(content)

    def post(self):
        title = self.request.get("title")
        entry_blog = self.request.get("entry_blog")
        error_title = self.request.get("error_title")
        error_entry = self.request.get("error_entry")
        if title == "":
            error_title = "Don't forget your title!"
        if entry_blog == "":
            error_entry = "Don't forget your blog content!"
        t = jinja_env.get_template("newpost.html")
        content = t.render(title=title, entry_blog=entry_blog, error_title=error_title, error_entry=error_entry)
        self.redirect("/newpost?title={0}&entry_blog={1}&error_title={2}&error_entry={3}".format(title,entry_blog,error_title,error_entry))

        if title and entry_blog:
            b = Blog(title=title, entry_blog=entry_blog)
            b.put()

            self.redirect("/blog")

class AllBlogs(Handler):
    def get(self):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created desc")
        t = jinja_env.get_template("front_page.html")
        content = t.render(blogs=blogs)
        self.response.write(content)

class ViewPostHandler(Handler):
    def get(self, id):
        blogs = db.GqlQuery("SELECT * FROM Blog where __key__ = {}".format(id))
        blog = Blog.get_by_id(int(id))
        bloglink = "/blog/{}".format(blog)
        t = jinja_env.get_template("blog.html")
        content = t.render(
                    blog=blog,
                    blogs=blogs,
                    bloglink=bloglink
                    )
        self.response.write(content)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/newpost', NewPost),
    ('/blog', RecentBlogs),
    ('/all', AllBlogs),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
