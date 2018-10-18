from home.models import PortfolioPage, TechnologiesPage, ContactPage


def menu_items(request):
    return {
        'menu_items': {
            "portfolio": PortfolioPage.objects.last(),
            "technology": TechnologiesPage.objects.last(),
        }
    }
