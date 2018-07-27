from home.models import HomePage, PortfolioPage, TechnologiesPage


def menu_items(request):
    return {
        'menu_items': [
            PortfolioPage.objects.last(),
            TechnologiesPage.objects.last(),
        ]
    }
