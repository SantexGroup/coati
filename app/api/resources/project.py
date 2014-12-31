__author__ = 'gastonrobledo'

from bson import json_util
from flask import jsonify, session
from flask.ext.restful import Resource, request
from mongoengine import DoesNotExist

from app.schemas import User, Project, Column, ProjectMember
from app.redis import RedisClient


class ProjectList(Resource):
    def __init__(self):
        super(ProjectList, self).__init__()

    def get(self, *args, **kwargs):
        return ProjectMember.get_projects_for_member(kwargs['user_id']['pk']), 200

    def post(self, *args, **kwargs):
        """
        Create Project
        """
        data = request.get_json(force=True, silent=True)
        if not data:
            msg = "payload must be a valid json"
            return jsonify({"error": msg}), 400
        try:
            user_id = kwargs['user_id']['pk']
            user = User.objects.get(pk=user_id)
        except DoesNotExist, e:
            return jsonify({"error": 'owner user does not exist'}), 400

        prj = Project(name=data.get('name'),
                      owner=user.to_dbref())
        prj.active = data.get('active')
        prj.private = data.get('private')
        prj.prefix = data.get('prefix') or data.get('name')[3:0]
        prj.description = data.get('description')

        # Add initial config
        prj.sprint_duration = 10
        prj.save()

        # add owner as member
        pm = ProjectMember(project=prj)
        pm.member = prj.owner
        pm.save()

        # Add 3 columns states
        col_names = ['ToDo', 'In Progress', 'Done']
        for index, c in enumerate(col_names):
            col = Column()
            col.title = c
            col.project = prj
            if index == len(col_names) - 1:
                col.done_column = True
            col.save()

        ## add to redis
        r = RedisClient(channel=str(prj.pk))
        r.store('new_project', **kwargs)

        return prj.to_json(), 201


class ProjectInstance(Resource):
    def __init__(self):
        super(ProjectInstance, self).__init__()

    def get(self, project_pk, *args, **kwargs):
        prj = Project.objects.get(pk=project_pk).select_related(max_depth=2)
        return prj.to_json(), 200

    def put(self, project_pk, *args, **kwargs):
        project = Project.objects.get(pk=project_pk)
        data = request.get_json(force=True, silent=True)
        if not data:
            msg = "payload must be a valid json"
            return jsonify({"error": msg}), 400
        project.active = data.get('active')
        project.description = data.get('description')
        project.name = data.get('name')
        owner = User.objects.get(id=data.get('owner_id'))
        project.owner = owner.to_dbref()
        project.private = data.get('private')
        project.sprint_duration = data.get('sprint_duration')
        project.prefix = data.get('prefix')
        project.save()

        ## add to redis
        r = RedisClient(channel=str(project.pk))
        r.store('update_project', **kwargs)

        return project.to_json(), 200

    def delete(self, project_pk, *args, **kwargs):
        project = Project.objects.get(pk=project_pk)
        project.delete()
        ## add to redis
        r = RedisClient()
        r.store('delete_project', **kwargs)
        return {}, 204


class ProjectColumns(Resource):
    def __init__(self):
        super(ProjectColumns, self).__init__()

    def get(self, project_pk, *args, **kwargs):
        return Column.objects(project=project_pk).order_by('order').to_json()

    def post(self, project_pk, *args, **kwargs):
        data = request.get_json(force=True, silent=True)
        if not data:
            msg = "payload must be a valid json"
            return jsonify({"error": msg}), 400
        project = Project.objects.get(pk=project_pk)

        col = Column()
        col.order = Column.objects.count()
        col.project = project
        col.title = data.get('title')
        col.color_max_cards = data.get('color_max_cards', '#FF0000')
        col.done_column = data.get('done_column', False)
        col.max_cards = data.get('max_cards', 9999)

        # Check if already exists one Done column
        if col.done_column:
            columns = Column.objects(project=project)
            for c in columns:
                if c.done_column:
                    c.done_column = False
                    c.save()
        col.save()

        ## add to redis
        r = RedisClient(channel=project_pk)
        r.store('new_column', **kwargs)

        return col.to_json(), 200


class ProjectColumn(Resource):
    def __init__(self):
        super(ProjectColumn, self).__init__()

    def get(self, column_pk, *args, **kwargs):
        return Column.objects.get(pk=column_pk).to_json()

    def put(self, column_pk, *args, **kwargs):
        col = Column.objects.get(pk=column_pk)
        data = request.get_json(force=True, silent=True)
        if col and data:
            col.title = data.get('title')
            col.color_max_cards = data.get('color_max_cards', '#FF0000')
            col.done_column = data.get('done_column', False)
            col.max_cards = data.get('max_cards', 9999)

            # check if there is another done column
            if col.done_column:
                columns = Column.objects(project=col.project, done_column=True)
                for c in columns:
                    c.done_column = False
                    c.save()
            col.save()
            ## add to redis
            r = RedisClient(channel=str(col.project.pk))
            r.store('update_column', **kwargs)
            return col.to_json(), 200
        return jsonify({"error": 'Bad Request'}), 400

    def delete(self, column_pk, *args, **kwargs):
        col = Column.objects.get(pk=column_pk)
        if col:
            ## add to redis
            r = RedisClient(channel=str(col.project.pk))
            r.store('delete_column', **kwargs)
            col.delete()
            return jsonify({"success": True}), 200
        return jsonify({"error": 'Bad Request'}), 400


class ProjectColumnsOrder(Resource):
    def __init__(self):
        super(ProjectColumnsOrder, self).__init__()

    def post(self, project_pk, *args, **kwargs):
        data = request.get_json(force=True, silent=True)
        if data:
            for index, c in enumerate(data):
                col = Column.objects.get(pk=c, project=project_pk)
                col.order = index
                col.save()
            ## add to redis
            r = RedisClient(channel=project_pk)
            r.store('order_columns', **kwargs)
            return jsonify({'success': True}), 200
        return jsonify({"error": 'Bad Request'}), 400


class ProjectMembers(Resource):
    def __init__(self):
        super(ProjectMembers, self).__init__()

    def get(self, project_pk, *args, **kwargs):
        return ProjectMember.objects(project=project_pk).to_json()

    def post(self, project_pk, *args, **kwargs):
        data = request.get_json(force=True, silent=True)
        if data:
            project = Project.objects.get(pk=project_pk)
            for member in data:
                if str(project.owner.pk) != member.get('value'):
                    m = ProjectMember(project=project_pk)
                    if member.get('value'):
                        m.member = User.objects.get(pk=member.get('value'))
                    else:
                        u = User(email=member.get('text'))
                        u.active = False
                        u.save()

                        # Send an email with the invitation
                        m.member = u
                    m.save()
            ## add to redis
            r = RedisClient(channel=project_pk)
            r.store('new_members', **kwargs)
            return jsonify({'success': True}), 200
        return jsonify({"error": 'Bad Request'}), 400