__author__ = 'gastonrobledo'
import math
from dateutil import parser
from datetime import timedelta, datetime
from flask import jsonify, request
from flask.ext.restful import Resource

from app.schemas import (Sprint, Project, SprintTicketOrder,
                         Column, TicketColumnTransition)


class SprintOrder(Resource):
    def __init__(self):
        super(SprintOrder, self).__init__()

    def post(self, project_pk, *args, **kwargs):
        data = request.get_json(force=True, silent=True)
        if data:
            for index, s in enumerate(data):
                sprint = Sprint.objects.get(pk=s)
                sprint.order = index
                sprint.save()
            return jsonify({'success': True}), 200
        return jsonify({"error": 'Bad Request'}), 400


class SprintList(Resource):
    def __init__(self):
        super(SprintList, self).__init__()

    def get(self, project_pk, *args, **kwargs):
        return Sprint.objects(project=project_pk).order_by('order').to_json()

    def post(self, project_pk, *args, **kwargs):
        """
        Create Sprint
        """
        try:
            project = Project.objects.get(id=project_pk)
        except Project.DoesNotExist, e:
            return jsonify({"error": 'project does not exist'}), 400
        total = Sprint.objects(project=project_pk).count()
        sp = Sprint(project=project.to_dbref())
        sp.name = 'Sprint %d' % (total + 1)
        sp.save()
        return sp.to_json(), 201


class SprintInstance(Resource):
    
    def __init__(self):
        super(SprintInstance, self).__init__()
    
    def get(self, sp_id, *args, **kwargs):
        sp = Sprint.objects.get(pk=sp_id)
        return sp.to_json, 200

    def put(self, sp_id, *args, **kwargs):
        data = request.get_json(force=True, silent=True)
        if data:
            sp = Sprint.objects.get(pk=sp_id)
            sp.name = data.get('name')
            if data.get('for_starting'):

                # sum all the ticket for the initial planning value
                sto = SprintTicketOrder.objects(sprint=sp)
                total_planned_points = 0
                for s in sto:
                    total_planned_points += s.ticket.points

                sp.total_points_when_started = total_planned_points
                sp.start_date = parser.parse(data.get('start_date'))
                sp.end_date = parser.parse(data.get('end_date'))
                sp.started = True
            sp.save()
            return sp.to_json(), 200
        return jsonify({"error": 'Bad Request'}), 400

    def delete(self, sp_id, *args, **kwargs):
        sp = Sprint.objects.get(pk=sp_id)
        sp.delete()
        return sp.to_json(), 204


class SprintActive(Resource):
    def __init__(self):
        super(SprintActive, self).__init__()

    def get(self, project_pk, *args, **kwargs):
        sprints = Sprint.objects(project=project_pk, started=True,
                                 finalized=False)
        sprint = None
        if sprints:
            sprint = sprints[0]
        if sprint:
            return sprint.to_json(), 200
        return jsonify({'started': False}), 404


class SprintTickets(Resource):

    def __init__(self):
        super(SprintTickets, self).__init__()

    def get(self, sprint_id, *args, **kwargs):
        sprint = Sprint.objects.get(pk=sprint_id)
        if sprint:
            return sprint.get_tickets_board_backlog()
        return jsonify({'error': 'Bad Request'}), 400


class SprintChart(Resource):

    def __init__(self):
        super(SprintChart, self).__init__()

    def get(self, sprint_id, *args, **kwargs):
        sprint = Sprint.objects.get(pk=sprint_id)
        if sprint:
            duration = sprint.project.sprint_duration
            planned = sprint.total_points_when_started
            # get done column
            col = Column.objects.get(project=sprint.project,
                                     done_column=True)
            sd = sprint.start_date
            days = []

            starting_points = 0

            tickets_sprint = SprintTicketOrder.objects(sprint=sprint)
            for tkt in tickets_sprint:
                starting_points += tkt.ticket.points

            points_remaining = []
            ideal = [planned]
            planned_counter = planned

            days.append(sd)
            counter = 1
            while len(days) <= duration:
                d = sd + timedelta(days=counter)
                if d.weekday() != 5 and d.weekday() != 6:
                    days.append(d)
                counter += 1

            for day in days:
                planned_counter = (planned_counter - planned / duration)
                if planned_counter > -1:
                    ideal.append(planned_counter)
                start_date = day
                end_date = start_date + timedelta(days=1)

                if start_date.date() <= datetime.now().date():

                    tct_list = TicketColumnTransition.objects(column=col,
                                                              when__gte=start_date.date(),
                                                              when__lte=end_date.date(),
                                                              latest_state=True)
                    points_burned_for_date = 0
                    for tct in tct_list:
                        points_burned_for_date += tct.ticket.points
                    starting_points -= points_burned_for_date
                    points_remaining.append(starting_points)

            #days.insert(0, 'Start')
            data = {
                'points_remaining': points_remaining,
                'dates': days,
                'ideal': ideal
            }
            return jsonify(data), 200
        return jsonify({'error': 'Bad Request'}), 400