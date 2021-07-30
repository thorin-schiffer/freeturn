from google.auth.exceptions import GoogleAuthError
from wagtail.admin import messages
from wagtail.contrib.modeladmin.helpers import PermissionHelper
from wagtail.contrib.modeladmin.options import ModelAdmin
from wagtail.contrib.modeladmin.views import IndexView

from crm import gmail_utils
from crm.models import ProjectMessage
import logging

logger = logging.getLogger(__file__)


class MessagePermissionHelper(PermissionHelper):
    def user_can_create(self, user):
        return False


class ProjectMessageIndexView(IndexView):
    def get_context_data(self, **kwargs):
        try:
            created_messages = gmail_utils.sync()
        except GoogleAuthError as ex:
            logger.error(f"Can't update messages: {ex}")
            messages.error(self.request, f"Can't update messages: {ex}")
            created_messages = []
        if created_messages:
            messages.info(
                self.request,
                f'{len(created_messages)} new messages'
            )
        return super().get_context_data(**kwargs)


class MessageAdmin(ModelAdmin):
    model = ProjectMessage
    menu_icon = 'fa-envelope-open'
    menu_label = 'Messages'
    list_display = ['subject', 'author', 'project', 'created']
    list_filter = ['project', 'author']
    ordering = ['-created']
    index_view_class = ProjectMessageIndexView
    inspect_view_enabled = True
    inspect_view_fields = ['project', 'subject', 'author', 'text']
    inspect_template_name = 'message_inspect.html'
    permission_helper_class = MessagePermissionHelper
    search_fields = ['subject',
                     'author__first_name',
                     'author__last_name',
                     'project__name',
                     'project__company__name']
