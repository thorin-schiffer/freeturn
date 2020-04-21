from django.utils.text import slugify
from pytest import mark


@mark.nondestructive
def test_home(selenium, base_url):
    selenium.get(base_url)
    assert selenium.find_element_by_id('main-avatar')
    assert selenium.find_element_by_id('github-link')
    assert selenium.find_element_by_id('stackoverflow-link')
    assert selenium.find_element_by_id('linkedin-link')


@mark.nondestructive
def test_portfolio_listing(selenium, base_url):
    selenium.get(base_url)
    portfolio_button = selenium.find_element_by_id('link-portfolio')
    portfolio_button.click()
    assert selenium.current_url == f"{base_url}/portfolio/"
    portfolio_items = selenium.find_elements_by_class_name('portfolio-item')
    assert len(portfolio_items) == 9
    assert "Portfolio" in selenium.find_element_by_xpath("//h1").text

    first_project = portfolio_items[0]
    first_project_name = first_project.find_element_by_xpath('//h4[@class="card-title"]').text
    first_project.find_element_by_xpath('.//a').click()

    assert selenium.current_url == f"{base_url}/portfolio/{slugify(first_project_name)}/"

    date = selenium.find_element_by_xpath("//h2")
    assert date.text
    assert selenium.find_element_by_id('position')
