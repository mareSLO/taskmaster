#!/usr/bin/env python
import os
import jinja2
import webapp2

from models import TaskMaster


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        template = jinja_env.get_template(view_filename)
        self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        tasks = TaskMaster.query(TaskMaster.completed == False,
                                  TaskMaster.deleted == False).order(TaskMaster.created).fetch()

        params = {"tasks": tasks}

        self.render_template("hello.html", params)


class NewTask(BaseHandler):
    def get(self):
        self.render_template("new-task.html")


class TaskAdd(BaseHandler):
    def post(self):
        task = self.request.get("task")
        description = self.request.get("description")
        complete_till = self.request.get("complete_till")

        if complete_till == "":
            complete_till = "Not specified"

        task1 = TaskMaster(task=task, description=description, complete_till=complete_till)
        task1.put()

        self.render_template("task-add.html")


class TaskHandler(BaseHandler):
    def get(self, task_id):
        task = TaskMaster.get_by_id(int(task_id))
        completed = self.request.get("completed")

        params = {"task": task, "completed": completed}

        self.render_template("task.html", params)


class CompletedTask(BaseHandler):
    def get(self):
        tasks = TaskMaster.query(TaskMaster.completed == True,
                                  TaskMaster.deleted == False).order(TaskMaster.created).fetch()

        params = {"tasks": tasks}

        self.render_template("completed-task.html", params)


class DeleteTask(BaseHandler):
    def get(self, task_id):
        task = TaskMaster.get_by_id(int(task_id))

        params = {"task": task}

        self.render_template("delete.html", params)

    def post(self, task_id):
        task = TaskMaster.get_by_id(int(task_id))

        task.deleted = True
        task.put()

        return self.redirect_to("home")


class EditTask(BaseHandler):
    def get(self, task_id):
        task = TaskMaster.get_by_id(int(task_id))

        params = {"task": task}

        self.render_template("edit.html", params)

    def post(self, task_id):
        edit_task = self.request.get("task2")
        edit_description = self.request.get("description2")
        edit_complete_till = self.request.get("complete_till2")

        task = TaskMaster.get_by_id(int(task_id))

        task.task = edit_task
        task.description = edit_description
        task.complete_till = edit_complete_till
        task.put()

        return self.redirect_to("home")


class CompleteHandler(BaseHandler):
    def get(self, task_id):
        task = TaskMaster.get_by_id(int(task_id))

        params = {"task": task}

        self.render_template("complete.html", params)

    def post(self, task_id):
        task = TaskMaster.get_by_id(int(task_id))

        task.completed = True
        task.put()

        return self.redirect_to("home")


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler, name="home"),
    webapp2.Route('/new-task', NewTask),
    webapp2.Route('/task-add', TaskAdd),
    webapp2.Route('/task/<task_id:\d+>', TaskHandler),
    webapp2.Route('/task/<task_id:\d+>/delete', DeleteTask),
    webapp2.Route('/task/<task_id:\d+>/edit', EditTask),
    webapp2.Route('/task/<task_id:\d+>/complete', CompleteHandler),
    webapp2.Route('/completed-task', CompletedTask),
], debug=True)