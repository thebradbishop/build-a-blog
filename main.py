#!/usr/bin/env python
import webapp2
import cgi
import jinja2
import os
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

def blog_key(name='default'):
    return db.Key.from_path('blogs', name)

def get_posts(limit, offset):
    blogs = Blog.all().order('-created').run(limit=limit,offset=offset)
    return blogs


class Blog(db.Model):
    title = db.StringProperty(required = True)
    entry_blog = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

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
        limit = self.request.get('limit')
        offset = self.request.get('offset')
        if limit == '':
            limit = 5
            offset = 0
        blogs = get_posts(limit,offset)
        t = jinja_env.get_template("front_page.html")
        content = t.render(blogs=blogs)
        self.response.write(content)

class RecentBlogs(Handler):
    def get(self):
        count = Blog.all().count()
        limit = 5
        offset = 0
        page=self.request.get('page')
        if page == '' or page == '1':
            page = 1
        if page > 1:
            offset = (int(page)*5)-5
        if count % limit == 0:
            pages = count/limit
        else:
            pages = (count/limit)+1
        page_count = range(1, pages+1, 1)
        blogs = get_posts(limit,offset)
        next_page = int(page) + 1
        previous_page = int(page) - 1
        if int(page) == int(pages):
            next_page = 0
        t = jinja_env.get_template("front_page.html")
        content = t.render(blogs=blogs, page=page, page_count=page_count, next_page=next_page, previous_page=previous_page, pages=pages)
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
            b = Blog(parent=blog_key(), title=title, entry_blog=entry_blog)
            b.put()

            self.redirect('blog/%s' %str(b.key().id()))

class AllBlogs(Handler):
    def get(self):
        blogs = Blog.all().order('-created')
        t = jinja_env.get_template("front_page.html")
        content = t.render(blogs=blogs)
        self.response.write(content)

class ViewPostHandler(Handler):
    def get(self, id):
        key = db.Key.from_path('Blog', int(id), parent=blog_key())
        blog = db.get(key)
        entry = id
        if not blog:
            t = jinja_env.get_template("error.html")
            content = t.render()
            self.response.write(content)
            return
        t = jinja_env.get_template("blog.html")
        content = t.render(blog=blog,entry=entry)
        self.response.write(content)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/newpost', NewPost),
    ('/blog', RecentBlogs),
    ('/all', AllBlogs),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
