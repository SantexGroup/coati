import json
from datetime import timedelta, datetime

from dateutil import parser
from flask import jsonify, request, g
from mongoengine import DoesNotExist

from app.core.models.sprint import Sprint, TicketColumnTransition, SprintTicket as SprintTicketOrder
from app.core.models.project import Project, Column
from app.core.models.ticket import Ticket
from app.web.api.resources.auth_resource import AuthResource
from app.utils import save_notification


class SprintOrder(AuthResource):
    def __init__(self):
        super(SprintOrder, self).__init__()

    def post(self, project_pk):
        data = request.get_json(force=True, silent=True)
        if data:
            for index, s in enumerate(data):
                sprint = Sprint.objects.get(pk=s)
                sprint.order = index
                sprint.save()
            # save activity
            save_notification(project_pk=project_pk,
                              verb='order_sprints',
                              data=data)

            return jsonify({'success': True}), 200
        return jsonify({"error": 'Bad Request'}), 400


class SprintList(AuthResource):
    def __init__(self):
        super(SprintList, self).__init__()

    def get(self, project_pk):
        return Sprint.objects(project=project_pk, finalized=False).order_by(
            'order').to_json()

    def post(self, project_pk):
        """
        Create Sprint
        """
        try:
            project = Project.objects.get(id=project_pk)
        except DoesNotExist, e:
            return jsonify({"error": 'project does not exist'}), 400
        total = Sprint.objects(project=project_pk).count()
        sp = Sprint(project=project.to_dbref())
        sp.name = 'Sprint %d' % (total + 1)
        sp.save()

        # save activity
        save_notification(project_pk=project_pk,
                          verb='new_sprint',
                          data=sp.to_dict())
        return sp.to_json(), 201


class SprintInstance(AuthResource):
    def __init__(self):
        super(SprintInstance, self).__init__()

    def get(self, project_pk, sp_id):
        sp = Sprint.objects.get(pk=sp_id)
        return sp.to_json(), 200

    def put(self, project_pk, sp_id):
        data = request.get_json(force=True, silent=True)
        if data:
            sp = Sprint.objects.get(pk=sp_id)
            sp.name = data.get('name', sp.name)

            if data.get('for_starting'):

                # sum all the ticket for the initial planning value
                sto = SprintTicketOrder.objects(sprint=sp, active=True)
                total_planned_points = 0
                for s in sto:
                    total_planned_points += s.ticket.points

                sp.total_points_when_started = total_planned_points

                sp.start_date = parser.parse(
                    data.get('start_date'))
                sp.end_date = parser.parse(data.get('end_date'))
                sp.started = True
            elif data.get('for_finalized'):
                sp.finalized = True
                tt = TicketColumnTransition.objects(sprint=sp,
                                                    latest_state=True)
                finished_tickets = []
                tickets_to_close_id = []
                for t in tt:
                    if t.column.done_column:
                        finished_tickets.append(t.ticket)
                        tickets_to_close_id.append(str(t.ticket.pk))

                all_not_finised = SprintTicketOrder.objects(
                    ticket__nin=finished_tickets,
                    sprint=sp,
                    active=True)
                all_not_finised.update(set__active=False)

                Ticket.objects(pk__in=tickets_to_close_id).update(
                    set__closed=True)
            elif data.get('for_editing'):
                sp.start_date = parser.parse(data.get('start_date'))
                sp.end_date = parser.parse(data.get('end_date'))
            sp.save()

            # save activity
            save_notification(project_pk=project_pk,
                              verb='update_sprint',
                              data=sp.to_dict())

            return sp.to_json(), 200

        return jsonify({"error": 'Bad Request'}), 400

    def delete(self, project_pk, sp_id):
        sp = Sprint.objects.get(pk=sp_id)

        # save activity
        save_notification(project_pk=project_pk,
                          verb='delete_sprint',
                          data=sp.to_dict())

        sp.delete()

        return sp.to_json(), 204


class SprintActive(AuthResource):
    def __init__(self):
        super(SprintActive, self).__init__()

    def get(self, project_pk):
        sprints = Sprint.objects(project=project_pk,
                                 started=True,
                                 finalized=False)
        sprint = None
        if sprints:
            sprint = sprints[0]
        if sprint:
            return sprint.to_json(), 200
        return jsonify({'started': False}), 200


class SprintTickets(AuthResource):
    def __init__(self):
        super(SprintTickets, self).__init__()

    def get(self, project_pk, sprint_id):
        sprint = Sprint.objects.get(pk=sprint_id)
        if sprint:
            return sprint.get_tickets_board_backlog()
        return jsonify({'error': 'Bad Request'}), 400


class SprintChart(AuthResource):
    def __init__(self):
        super(SprintChart, self).__init__()

    def get(self, project_pk, sprint_id):
        sprint = Sprint.objects.get(pk=sprint_id)
        if sprint:
            # include the weekends??
            weekends = bool(request.args.get('weekends', False))
            # get tickets of the sprint
            tickets_in_sprint = SprintTicketOrder.objects(sprint=sprint,
                                                          active=(sprint.started and not sprint.finalized))
            # get the points planned when it started
            planned_sprint_points = sprint.total_points_when_started

            # get the sum of points of the entire sprint
            y1_total_sprint_points = 0
            if tickets_in_sprint:
                for sto in tickets_in_sprint:
                    y1_total_sprint_points += sto.ticket_repr.get('points')

            if planned_sprint_points > y1_total_sprint_points:
                planned_sprint_points = y1_total_sprint_points

            # get done column
            col = Column.objects.get(project=sprint.project,
                                     done_column=True)

            # define the lists
            days = []
            points_remaining = []
            ideal_planned = [y1_total_sprint_points]
            ideal_real = [y1_total_sprint_points]

            # add the first date, the sprint started date
            days.append(sprint.start_date)
            # get the duration in days of the sprint
            duration = (sprint.end_date - sprint.start_date).days

            # get the dates of the sprint
            counter = 1
            while counter <= duration:
                d = sprint.start_date + timedelta(days=counter)
                if d.date() <= sprint.end_date.date():
                    if weekends:
                        if d.weekday() != 5 and d.weekday() != 6:
                            continue
                    days.append(d)
                counter += 1

            # calculate deltas for ideal lines
            delta_planned = float(y1_total_sprint_points) / float(duration)
            delta_real = float(y1_total_sprint_points) / float(duration)
            # define initial counters
            planned_counter = y1_total_sprint_points
            real_counter = y1_total_sprint_points
            starting_points = planned_sprint_points

            # get team velocity
            x2_limit_date = datetime.now()
            if datetime.now() > sprint.end_date:
                x2_limit_date = sprint.end_date
            total_burned_points = 0
            tickets_done = TicketColumnTransition.objects(column=col,
                                                          sprint=sprint,
                                                          when__gte=sprint.start_date,
                                                          when__lte=x2_limit_date,
                                                          latest_state=True)

            for td in tickets_done:
                spo_done = SprintTicketOrder.objects.get(ticket=td.ticket,
                                                         sprint=sprint)
                total_burned_points += spo_done.ticket_repr.get('points')
            # adding 1 day to include limits
            used_days = (x2_limit_date.date() - sprint.start_date.date()).days
            if used_days < 1:
                velocity = float(y1_total_sprint_points) / float(duration)
            else:
                y2_remaining_points = y1_total_sprint_points - total_burned_points
                velocity = float(
                    y1_total_sprint_points - y2_remaining_points) / float(used_days)
            delta_real = velocity or delta_real

            eta = y1_total_sprint_points / delta_real

            # list of formatted dates
            formatted_days = []
            # tickets added o burned
            tickets = []
            # iterate each day to see the burned or added points
            for day in days:
                planned_counter -= delta_planned
                real_counter -= delta_real
                if planned_counter > 0:
                    ideal_planned.append(round(planned_counter, 2))
                else:
                    ideal_planned.append(0)
                if real_counter > 0:
                    ideal_real.append(round(real_counter, 2))
                else:
                    ideal_real.append(0)
                # format the dates
                formatted_days.append(datetime.strftime(day, '%d %a, %b %Y'))
                start_date = day if sprint.start_date < day else sprint.start_date
                end_date = (start_date + timedelta(hours=23, minutes=59)).date()

                if start_date.date() <= x2_limit_date.date():

                    points_burned_for_date = 0
                    points_added = 0
                    # get tickets after started sprint
                    filters = dict(sprint=sprint,
                                   when__gt=start_date,
                                   when__lt=end_date)
                    if start_date > sprint.start_date:
                        filters.update(dict(when__gt=start_date.date()))

                    spt_list = SprintTicketOrder.objects(**filters)
                    for spt in spt_list:
                        tickets.append(
                            u'Added: %s-%s (%s)' % (spt.ticket.project.prefix,
                                                    spt.ticket.number,
                                                    spt.ticket.points))
                        points_added += spt.ticket_repr.get('points')

                    # get tickets in done column
                    tct_list = TicketColumnTransition.objects(column=col,
                                                              sprint=sprint,
                                                              when__gte=start_date.date(),
                                                              when__lt=end_date,
                                                              latest_state=True)

                    for tct in tct_list:
                        spo = SprintTicketOrder.objects.get(ticket=tct.ticket,
                                                            sprint=sprint)
                        tickets.append(
                            u'Burned: %s-%s (%s)' % (tct.ticket.project.prefix,
                                                     tct.ticket.number,
                                                     spo.ticket_repr.get('points')))
                        points_burned_for_date += spo.ticket_repr.get('points')

                    if points_burned_for_date > 0:
                        starting_points -= points_burned_for_date
                    if points_added > 0:
                        starting_points += points_added

                    points_remaining.append(starting_points)

            data = {
                'points_remaining': points_remaining,
                'tickets': tickets,
                'dates': formatted_days,
                'ideal_planned': ideal_planned,
                'ideal_real': ideal_real,
                'eta': sprint.start_date + timedelta(days=eta),
                'velocity': delta_real,
                'planned_points': sprint.total_points_when_started,
                'all_tickets': json.loads(
                    sprint.get_tickets_with_latest_status())
            }
            return jsonify(data), 200
        return jsonify({'error': 'Bad Request'}), 400


class SprintArchivedList(AuthResource):
    def __init__(self):
        super(SprintArchivedList, self).__init__()

    def get(self, project_pk):
        return Sprint.objects(project=project_pk, finalized=True).order_by(
            'order').to_json(archived=True)


class SprintAllList(AuthResource):
    def __init__(self):
        super(SprintAllList, self).__init__()

    def get(self, project_pk):
        return Sprint.objects(project=project_pk).order_by('order').to_json()
