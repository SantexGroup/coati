from flask import Flask
from unittest import TestCase
from app import core
from app.core.models.project import Project


class TestProjects(TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['MONGODB_DATABASE'] = 'coati'
        core.init_app(self.app)

    def test_project_list(self):
        with self.app.app_context():
            prj = core.db.Project()
            prj.name = 'Testing Project'
            prj.owner = core.db.User.one({
                'email': 'gaston.robledo@santexgroup.com'
            }).get_dbref()
            if prj.validate():
                prj.save()