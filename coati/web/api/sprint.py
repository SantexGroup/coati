import json
from datetime import timedelta, datetime

from dateutil import parser
from flask import jsonify, request

from coati.core.models.sprint import (Sprint, SprintTicketOrder,
                                      TicketColumnTransition as TicketCT)
from coati.core.models.project import Column
from coati.core.models.ticket import Ticket, Comment
from coati.web.api import errors as api_errors
from coati.web.api.auth import AuthResource
from coati.web.utils import save_notification
from coati.web.api.project import get_project_request


def get_sprint_request(sprint_id):
    sprint = Sprint.get_by_id(sprint_id)
    if not sprint:
        raise api_errors.MissingResource(
            api_errors.INVALID_SPRINT_MSG
        )
    return sprint


class SprintOrder(AuthResource):
    """
    Order Sprints in a Project
    """

    def post(self, project_pk):
        """
        Order sprints in a project

        :param project_pk: Project ID
        :return: Order
        """
        data = request.get_json(silent=True)
        if not data:
            raise api_errors.InvalidAPIUsage(
                api_errors.INVALID_JSON_BODY_MSG
            )

        Sprint.order_items(data)
        # save activity
        save_notification(project_pk=project_pk,
                          verb='order_sprints',
                          data=data)
        return data, 200


class SprintList(AuthResource):
    """
    Get List of Sprints
    """

    def get(self, project_pk):
        """
        Get List of Sprints by Project
        :param project_pk: Project ID
        :return:
        """
        prj = get_project_request(project_pk)
        return Sprint.get_by_project_not_finalized(prj), 200

    def post(self, project_pk):
        """
        Create a Sprint for a Project
        """
        project = get_project_request(project_pk)
        total = Sprint.objects(project=project).count()
        sp = Sprint(project=project)
        sp.name = 'Sprint %d' % (total + 1)
        sp.save()

        # save activity
        save_notification(project_pk=project_pk,
                          verb='new_sprint',
                          data=sp.to_dict())

        return sp, 201


class SprintInstance(AuthResource):
    """
    Sprint Resource Instance
    """

    def get(self, project_pk, sp_id):
        """
        Get a Sprint Instance
        :param project_pk: Project ID
        :param sp_id: Sprint ID
        :return: Sprint Object
        """
        get_project_request(project_pk)
        sp = get_sprint_request(sp_id)
        return sp, 200

    def put(self, project_pk, sp_id):
        """
        Update a Sprint
        :param project_pk:
        :param sp_id:
        :return:
        """
        get_project_request(project_pk)
        data = request.get_json(silent=True)
        if not data:
            raise api_errors.InvalidAPIUsage(
                api_errors.INVALID_JSON_BODY_MSG
            )

        sp = get_sprint_request(sp_id)
        sp.name = data.get('name', sp.name)

        if data.get('for_starting'):
            # sum all the ticket for the initial planning value
            sto = SprintTicketOrder.get_active_sprint(sp)
            total_planned_points = 0
            if sto:
                # get the sum of points
                for s in sto:
                    total_planned_points += s.ticket.points

            sp.total_points_when_started = total_planned_points

            sp.start_date = parser.parse(data.get('start_date'))
            sp.end_date = parser.parse(data.get('end_date'))
            sp.started = True

        elif data.get('for_finalized'):
            # Mark as finalized
            sp.finalized = True

            # Get tickets in Done column
            finished_tickets = []
            tickets_to_close_id = []
            tt = TicketCT.get_transitions_for_sprint(sp)

            for t in tt:
                if t.column.done_column:
                    finished_tickets.append(t.ticket)
                    tickets_to_close_id.append(str(t.ticket.pk))

            # Deactivate Tickets
            SprintTicketOrder.inactivate_list_spo(sp, finished_tickets)
            # Close Tickets
            Ticket.close_tickets(tickets_to_close_id)

        elif data.get('for_editing'):
            sp.start_date = parser.parse(data.get('start_date'))
            sp.end_date = parser.parse(data.get('end_date'))

        sp.save()

        # save activity
        save_notification(project_pk=project_pk,
                          verb='update_sprint',
                          data=sp.to_dict())

        return sp, 200

    def delete(self, project_pk, sp_id):
        """
        Delete Sprint
        :param project_pk: Project ID
        :param sp_id: Sprint ID
        :return: Nothing
        """
        get_project_request(project_pk)
        sp = get_sprint_request(sp_id)
        # save activity
        save_notification(project_pk=project_pk,
                          verb='delete_sprint',
                          data=sp.to_dict())

        sp.delete()

        return {}, 204


class SprintActive(AuthResource):
    """
    Active Sprint
    """

    def get(self, project_pk):
        """
        Get Active Sprint by Project
        :param project_pk: ProjectID
        :return: Sprint Object
        """
        prj = get_project_request(project_pk)
        sprint = Sprint.get_active_sprint(prj)
        return sprint, 200


class SprintTickets(AuthResource):
    """
    Get Tickets for a Sprint
    """

    def get(self, project_pk, sprint_id):
        """
        Get tickets fro a Sprint
        :param project_pk: Project ID
        :param sprint_id: Sprint ID
        :return: List of Tickets
        """

        prj = get_project_request(project_pk)
        sprint = get_sprint_request(sprint_id)

        # first get all the columns
        ticket_list = []
        columns = Column.get_by_project(prj)

        if columns:
            ticket_transitions = TicketCT.get_transitions_in_cols(columns)
            tickets_in_cols = []
            for tt in ticket_transitions:
                tickets_in_cols.append(tt.ticket)

            # exclude from sprint
            tickets = SprintTicketOrder.list_spo(sprint, tickets_in_cols)

            for t in tickets:
                if t.ticket.__class__.__name__ != 'DBRef':
                    tkt = t.ticket_repr
                    tkt['order'] = t.order
                    tkt['badges'] = {
                        'comments': Comment.get_by_ticket(t.ticket).count(),
                        'files': len(t.ticket.files)
                    }
                    assignments = []
                    for ass in t.ticket.assigned_to:
                        if ass.__class__.__name__ != 'DBRef':
                            val = ass.to_dict()
                            val['member'] = ass.member.to_dict()
                            assignments.append(val)
                    tkt['assigned_to'] = assignments
                    ticket_list.append(tkt)
        return ticket_list, 200


class SprintChart(AuthResource):
    """
    Get Burndown chart for a Sprint
    """

    def get(self, project_pk, sprint_id):
        prj = get_project_request(project_pk)
        sprint = get_sprint_request(sprint_id)
        if sprint:
            # include the weekends??
            weekends = bool(request.args.get('weekends', False))
            # get tickets of the sprint
            tickets_in_sprint = SprintTicketOrder.objects(sprint=sprint,
                                                          active=(
                                                              sprint.started and not sprint.finalized))
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
            tickets_done = TicketCT.objects(column=col,
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
                    y1_total_sprint_points - y2_remaining_points) / float(
                    used_days)
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
                    tct_list = TicketCT.objects(column=col,
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
                                                     spo.ticket_repr.get(
                                                         'points')))
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
            return data, 200
        return {'error': 'Bad Request'}, 400


class SprintArchivedList(AuthResource):
    """
    Get Sprints Archived
    """

    def get(self, project_pk):
        """
        Get List of archived sprints
        :param project_pk: Project ID
        :return: List of sprints
        """
        prj = get_project_request(project_pk)
        return Sprint.get_archived_sprints(prj).to_json(), 200


class SprintAllList(AuthResource):
    """
    Get All Sprints
    """

    def get(self, project_pk):
        """
        Get List of sprints
        :param project_pk: Project ID
        :return: List of sprints
        """
        prj = get_project_request(project_pk)
        return Sprint.objects(project=prj).order_by('order').to_json()
