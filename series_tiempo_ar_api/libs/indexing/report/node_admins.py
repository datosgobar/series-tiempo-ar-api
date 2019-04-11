from django.conf import settings
from django.contrib.auth.models import Group


class NodeAdmins:

    def __init__(self, node):
        self.node = node

    def get_emails(self):
        return [admin.email for admin in self.node.admins.all() if admin.email is not None]


class GlobalAdmins:
    def __init__(self):
        self.admins = Group.objects.get(name=settings.READ_DATAJSON_RECIPIENT_GROUP).user_set.all()

    def get_emails(self):
        return [admin.email for admin in self.admins if admin.email is not None]
