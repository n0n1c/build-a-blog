#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    title = db.StringProperty(required = True)
    blog = db.TextProperty(required = True)
    posted = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def get(self):
        self.render("homepage.html")

class BlogPage(Handler):
    def get(self):
        title = self.request.get("title")
        blog = self.request.get("blogpost")
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY posted DESC LIMIT 5")

        self.render("blogpost.html", title=title, blog=blog, blogs=blogs)

    def post(self):
        title = self.request.get("title")
        blog = self.request.get("blogpost")
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY posted DESC LIMIT 5")

        if title and blog:
            b = Blog(title = title, blog = blog)
            b.put()
            post_id = b.key().id()

            self.redirect("/blog/" + str(post_id))

        else:
            error = "You need to have a title and a blogpost!"
            self.render("homepage.html", title=title, blog=blog, error=error)

class ViewPostHandler(Handler):
    def get(self, id):
        blog_id = Blog.get_by_id(int(id))

        if blog_id:
            self.render("singlepost.html", blog_id=blog_id)

        else:
            error = "It looks like that blog doesn't exist. YET..."
            self.render("homepage.html", error=error)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', BlogPage),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
