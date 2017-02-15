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

template_dir = os.path.join(os.path.dirname(__file__),'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),autoescape =True)


class Handler(webapp2.RequestHandler):
    def write(self, *a,**kw):
        self.response.write(*a,**kw)

    def render_str(self,template,**params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self,template,**kw):
        self.write(self.render_str(template,**kw))


class Blog(db.Model):
    title = db.StringProperty(required =True)
    blogpost = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainHandler(Handler):
     def get(self):
         self.render("welcomepage.html")


class NewPostHandler(Handler):
    def render_front(self,title ="",blogpost = "",error=""):
        self.render("blog-front-page.html",title = title,blogpost = blogpost,error= error )
    def get(self):
        self.render_front()

    def post(self):
         title = self.request.get("title")
         blogpost = self.request.get("blogpost")
         if title and blogpost :
             blog =Blog(title = title,blogpost = blogpost)
             blog.put()
             page= str(blog.key().id())
             self.redirect('/blog/'+page)
         else:
             error = "Please enter a title and content!! Both fields are mandatory"
             self.render_front(title,blogpost,error)


class PostHandler(Handler):
        def render_front(self):
            blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5 ")
            self.render("blog-post-page.html",blogs = blogs )

        def get(self):
            self.render_front()

class ViewPostHandler(webapp2.RequestHandler):

    def get(self, id):
        blog =Blog.get_by_id (int(id))
        if  not blog:

            self.renderError(404)
        else:
             t = jinja_env.get_template('viewpost.html')
             content = t.render(blog = blog)
             self.response.write(content)

app = webapp2.WSGIApplication([
    ('/',MainHandler),
    ('/blog',PostHandler),
    ('/newpost',NewPostHandler),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler),
], debug=True)
