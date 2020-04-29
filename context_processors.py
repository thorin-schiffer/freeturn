from home.models import PortfolioPage, TechnologiesPage, ContactPage, HomePage
from utils import disabled_in_admin


@disabled_in_admin
def menu_items(request):
    return {
        'menu_items': {
            'portfolio': PortfolioPage.objects.last(),
            'technology': TechnologiesPage.objects.last(),
            **{
                page.title: page for page in ContactPage.objects.live()
            }
        },
        'footer': HomePage.objects.live().first().title
    }
