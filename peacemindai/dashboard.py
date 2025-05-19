from django.utils.translation import gettext_lazy as _
from jet.dashboard import modules
from jet.dashboard.dashboard import Dashboard, AppIndexDashboard

class CustomIndexDashboard(Dashboard):
    columns = 3

    def init_with_context(self, context):
        self.available_children.append(modules.ModelList)
        self.available_children.append(modules.RecentActions)
        self.available_children.append(modules.Feed)
        self.available_children.append(modules.LinkList)

        # First column
        self.children.append(modules.ModelList(
            _('Users'),
            models=('users.*', 'auth.*'),
            column=0,
            order=0
        ))
        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            10,
            column=0,
            order=1
        ))

        # Second column
        self.children.append(modules.ModelList(
            _('Chat'),
            models=('chat.*',),
            column=1,
            order=0
        ))
        self.children.append(modules.Feed(
            _('Latest Django News'),
            feed_url='https://www.djangoproject.com/rss/weblog/',
            limit=5,
            column=1,
            order=1
        ))

        # Third column
        self.children.append(modules.ModelList(
            _('Main App'),
            models=('main_app.*',),
            column=2,
            order=0
        ))
        self.children.append(modules.LinkList(
            _('Quick Links'),
            children=[
                {
                    'title': _('PeaceMindAI Home'),
                    'url': '/',
                    'external': False,
                },
                {
                    'title': _('About'),
                    'url': '/about/',
                    'external': False,
                },
                {
                    'title': _('Chat Lobby'),
                    'url': '/chat/lobby/',
                    'external': False,
                },
            ],
            column=2,
            order=1
        ))

class CustomAppIndexDashboard(AppIndexDashboard):
    def init_with_context(self, context):
        self.available_children.append(modules.ModelList)
        self.available_children.append(modules.RecentActions)

        # First column
        self.children.append(modules.ModelList(
            _('Application Models'),
            models=self.models(),
            column=0,
            order=0
        ))

        # Second column
        self.children.append(modules.RecentActions(
            _('Recent Actions'),
            5,
            column=1,
            order=0
        )) 