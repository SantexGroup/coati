import json
import urllib2
import base64

from flask import jsonify
from flask.ext.restful import request
from mongoengine import DoesNotExist

from app.schemas import User, Project, Column, ProjectMember, Ticket, \
    Attachment
from app.api.resources.auth_resource import AuthResource
from app.utils import send_new_member_email_async, save_notification


class ProjectList(AuthResource):
    def __init__(self):
        super(ProjectList, self).__init__()

    def get(self, *args, **kwargs):
        return ProjectMember.get_projects_for_member(
            kwargs['user_id']['pk']), 200

    def post(self, *args, **kwargs):
        """
        Create Project
        """
        user_id = kwargs['user_id']['pk']
        data = request.get_json(force=True, silent=True)
        if not data:
            msg = "payload must be a valid json"
            return jsonify({"error": msg}), 400
        try:
            user = User.objects.get(pk=user_id)
        except DoesNotExist, e:
            return jsonify({"error": 'owner user does not exist'}), 400

        prj = Project(name=data.get('name'),
                      owner=user.to_dbref())
        prj.active = data.get('active')
        prj.private = data.get('private')
        prj.prefix = data.get('prefix', data.get('name')[:3].upper())
        prj.description = data.get('description')

        # Add initial config
        prj.sprint_duration = 10
        prj.save()

        # add owner as member
        pm = ProjectMember(project=prj)
        pm.member = prj.owner
        pm.is_owner = True
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

        # save activity
        save_notification(project_pk=prj.pk,
                          author=kwargs['user_id']['pk'],
                          verb='new_project')

        return prj.to_json(), 201


class ProjectInstance(AuthResource):
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
        project.project_type = 'S' if data.get('project_type', 'S') else 'S'
        project.save()

        # save activity
        save_notification(project_pk=project.pk,
                          author=kwargs['user_id']['pk'],
                          verb='update_project')

        return project.to_json(), 200

    def delete(self, project_pk, *args, **kwargs):
        project = Project.objects.get(pk=project_pk)
        project.delete()
        return jsonify({}), 204


class ProjectColumns(AuthResource):
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

        # save activity
        save_notification(project_pk=project.pk,
                          author=kwargs['user_id']['pk'],
                          verb='new_column',
                          data=col.to_json())

        return col.to_json(), 200


class ProjectColumn(AuthResource):
    def __init__(self):
        super(ProjectColumn, self).__init__()

    def get(self, project_pk, column_pk, *args, **kwargs):
        return Column.objects.get(pk=column_pk).to_json()

    def put(self, project_pk, column_pk, *args, **kwargs):
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

            # save activity
            save_notification(project_pk=col.project.pk,
                              author=kwargs['user_id']['pk'],
                              verb='update_column',
                              data=col.to_json())

            return col.to_json(), 200
        return jsonify({"error": 'Bad Request'}), 400

    def delete(self, project_pk, column_pk, *args, **kwargs):
        col = Column.objects.get(pk=column_pk)
        if col:
            # save activity
            save_notification(project_pk=col.project.pk,
                              author=kwargs['user_id']['pk'],
                              verb='delete_column',
                              data=col.to_json())

            col.delete()
            return jsonify({"success": True}), 200
        return jsonify({"error": 'Bad Request'}), 400


class ProjectColumnsOrder(AuthResource):
    def __init__(self):
        super(ProjectColumnsOrder, self).__init__()

    def post(self, project_pk, *args, **kwargs):
        data = request.get_json(force=True, silent=True)
        if data:
            for index, c in enumerate(data):
                col = Column.objects.get(pk=c, project=project_pk)
                col.order = index
                col.save()

            # save activity
            save_notification(project_pk=project_pk,
                              author=kwargs['user_id']['pk'],
                              verb='order_columns',
                              data=data)
            return jsonify({'success': True}), 200
        return jsonify({"error": 'Bad Request'}), 400


class ProjectMembers(AuthResource):
    def __init__(self):
        super(ProjectMembers, self).__init__()

    def get(self, project_pk, *args, **kwargs):
        return ProjectMember.objects(project=project_pk).to_json()

    def put(self, project_pk, *args, **kwargs):
        data = request.get_json(force=True, silent=True)
        if data:
            try:
                pm = ProjectMember.objects.get(pk=data.get('member'))
                project = Project.objects.get(pk=project_pk)
                pm.is_owner = True
                project.owner = pm.member
                ProjectMember.objects(project=project_pk).update(
                    set__is_owner=False)
                pm.save()
                return jsonify({'success': True}), 200
            except DoesNotExist:
                return jsonify({'error': 'Not Found'}), 404

        return jsonify({'error': 'Bad Request'}), 400

    def delete(self, project_pk, *args, **kwargs):
        data = request.get_json(force=True, silent=True)
        if data:
            try:
                pm = ProjectMember.objects.get(pk=data.get('member'))
                pm.delete()
                return jsonify({'success': True}), 200
            except DoesNotExist:
                return jsonify({'error': 'Not Found'}), 404

        return jsonify({'error': 'Bad Request'}), 400

    def post(self, project_pk, *args, **kwargs):
        data = request.get_json(force=True, silent=True)
        if data:
            project = Project.objects.get(pk=project_pk)
            members_added = []
            for member in data:
                if str(project.owner.pk) != member.get('value'):
                    exists = ProjectMember.objects(project=project_pk,
                                                   member=member.get('value'))
                    if exists.count() < 1:

                        m = ProjectMember(project=project_pk)
                        if member.get('value'):
                            m.member = User.objects.get(pk=member.get('value'))

                        else:
                            u = User(email=member.get('text'))
                            u.active = False
                            u.save()
                            m.member = u

                        m.save()
                        # Send email notification
                        send_new_member_email_async(m.member, project)
                        members_added.append(m.to_json())
                    else:
                        return jsonify({'success': False,
                                        'message': 'Already added'}), 200
            # save activity
            save_notification(project_pk=project_pk,
                              author=kwargs['user_id']['pk'],
                              verb='new_members',
                              data={'members': members_added})
            return jsonify({'success': True}), 200
        return jsonify({"error": 'Bad Request'}), 400


class ProjectImport(AuthResource):
    def __init__(self):
        super(ProjectImport, self).__init__()

    def post(self, project_pk, *args, **kwargs):
        """
        Import cards and columns
        """
        body = request.form
        imported_file = request.files.get('file')
        if not imported_file and not body:
            msg = "payload must be a valid file"
            return jsonify({"error": msg}), 400
        try:
            project = Project.objects.get(pk=project_pk)
        except DoesNotExist, e:
            return jsonify({"error": 'project does not exist'}), 400

        data = json.loads(imported_file.stream.read().decode('utf-8'),
                          encoding='UTF-8')
        tickets = []
        actual_last_ticket = Ticket.objects(project=project).order_by('-number')
        starting_number = actual_last_ticket.first().number if actual_last_ticket else 1
        if body.get('include_cards') == u'true':
            for card in data.get('cards'):
                t = Ticket()
                t.title = card.get('name')
                t.description = card.get('desc')
                t.labels = [l.get('name') for l in card.get('labels')]
                t.closed = card.get('closed')

                for att in card.get('attachments'):
                    location = att.get('url')
                    if 'https://trello-attachments.s3.amazonaws.com/' in location:
                        file_location = urllib2.urlopen(location)
                        file_data = file_location.read()
                        if file_data:
                            att_file = Attachment()
                            att_file.name = att.get('name')
                            att_file.size = att.get('bytes')
                            att_file.type = att.get('mimeType')
                            att_file.data = base64.b64encode(file_data)
                            att_file.save()
                            t.files.append(att_file)
                t.project = project
                t.number = starting_number
                t.order = starting_number - 1
                # by default user story
                t.type = 'U'
                t.points = 0
                tickets.append(t)
                starting_number += 1

        columns = []
        if body.get('include_cols') == u'true':
            for col in data.get('lists'):
                if not col.get('closed'):
                    new_col = Column()
                    new_col.title = col.get('name')
                    new_col.project = project
                    columns.append(new_col)

        if tickets:
            Ticket.objects.insert(tickets, load_bulk=False)
        if columns:
            Column.objects.insert(columns, load_bulk=False)

        # save activity
        save_notification(project_pk=project_pk,
                          author=kwargs['user_id']['pk'],
                          verb='import',
                          data=data)

        return jsonify({'success': True}), 200