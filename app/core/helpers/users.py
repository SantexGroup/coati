from bson import json_util


def user_notification_to_json(user_instance):
    data = user_instance.to_dict()
    if user_instance.activity.__class__.__name__ != 'DBRef':
        data['activity'] = user_instance.activity.to_dict()
        data['activity']['project'] = user_instance.activity.project.to_dict()
        data['activity']['author'] = user_instance.activity.author.to_dict()
        data['activity']['data'] = user_instance.activity.data
    return json_util.dumps(data)
