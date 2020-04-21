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

    last_project = portfolio_items[0]
    last_project_name = last_project.find_element_by_xpath('//h4[@class="card-title"]').text
    last_project.find_element_by_xpath('.//a').click()

    assert selenium.current_url == f"{base_url}/portfolio/{slugify(last_project_name)}/"

    date = selenium.find_element_by_xpath("//h2")
    assert date.text
    assert selenium.find_element_by_id('position').text.strip()
    assert selenium.find_element_by_id('responsibilities').text.strip()
    assert selenium.find_element_by_id('project-link').get_attribute('href')

    technology_links = selenium.find_elements_by_xpath('//a[contains(@id, "technology-")]')
    assert technology_links

    selenium.find_element_by_id('back').click()
    assert selenium.current_url == f"{base_url}/portfolio/"


@mark.nondestructive
def test_current_project(selenium, base_url):
    selenium.get(base_url)

    portfolio_button = selenium.find_element_by_id('link-portfolio')
    portfolio_button.click()
    last_project = selenium.find_elements_by_class_name('portfolio-item')[0]
    last_project_name = last_project.find_element_by_xpath('//h4[@class="card-title"]').text

    home_button = selenium.find_element_by_class_name('navbar-brand')
    home_button.click()
    assert selenium.current_url == f"{base_url}/"

    current_project_button = selenium.find_element_by_id('link-current-project')
    current_project_button.click()
    assert selenium.find_element_by_xpath('//h1').text == last_project_name
