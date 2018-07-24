from home.models import HomePage, PortfolioPage


def menu_items(request):
    return {
        'menu_items': [
            HomePage.objects.last(),
            PortfolioPage.objects.last()
        ]
    }
