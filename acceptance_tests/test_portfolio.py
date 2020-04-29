import time

from django.utils.text import slugify


def test_home(selenium, base_url):
    selenium.get(base_url)
    assert selenium.find_element_by_id('main-avatar')
    assert selenium.find_element_by_id('github-link')
    assert selenium.find_element_by_id('stackoverflow-link')
    assert selenium.find_element_by_id('linkedin-link')


def test_portfolio_listing(selenium, base_url):
    selenium.get(base_url)
    portfolio_button = selenium.find_element_by_id('link-portfolio')
    portfolio_button.click()
    assert selenium.current_url == f'{base_url}/portfolio/'
    portfolio_items = selenium.find_elements_by_class_name('portfolio-item')
    assert len(portfolio_items) == 9
    assert 'Portfolio' in selenium.find_element_by_xpath('//h1').text

    last_project = portfolio_items[0]
    last_project_name = last_project.find_element_by_xpath('//h4[@class="card-title"]').text
    last_project.find_element_by_xpath('.//a').click()

    assert selenium.current_url == f'{base_url}/portfolio/{slugify(last_project_name)}/'

    date = selenium.find_element_by_xpath('//h2')
    assert date.text
    assert selenium.find_element_by_id('position').text.strip()
    assert selenium.find_element_by_id('responsibilities').text.strip()
    assert selenium.find_element_by_id('project-link').get_attribute('href')

    technology_links = selenium.find_elements_by_xpath('//a[contains(@id, "technology-")]')
    assert technology_links

    selenium.find_element_by_id('back').click()
    assert selenium.current_url == f'{base_url}/portfolio/'


def test_current_project(selenium, base_url):
    selenium.get(base_url)

    portfolio_button = selenium.find_element_by_id('link-portfolio')
    portfolio_button.click()
    last_project = selenium.find_elements_by_class_name('portfolio-item')[0]
    last_project_name = last_project.find_element_by_xpath('//h4[@class="card-title"]').text

    home_button = selenium.find_element_by_class_name('navbar-brand')
    home_button.click()
    assert selenium.current_url == f'{base_url}/'

    current_project_button = selenium.find_element_by_id('link-current-project')
    current_project_button.click()
    assert selenium.find_element_by_xpath('//h1').text == last_project_name


def admin_login(selenium, base_url):
    selenium.get(f'{base_url}/admin/login/')
    selenium.find_element_by_name('username').send_keys('admin')
    selenium.find_element_by_name('password').send_keys('admin')
    selenium.find_element_by_xpath("//*[@type='submit']").submit()
    time.sleep(1)
    assert selenium.current_url == f'{base_url}/admin/'


def test_contact(selenium, base_url, faker):
    selenium.get(base_url)
    portfolio_button = selenium.find_element_by_id('form-contact')
    portfolio_button.click()
    assert selenium.current_url == f'{base_url}/contact/'
    input_element = selenium.find_element_by_name('some-words-about-your-project')
    input_element.clear()
    text = faker.word()
    input_element.send_keys(text)
    selenium.execute_script('window.scrollTo(0, document.body.scrollHeight)')
    selenium.find_element_by_name('privacy-policy').click()
    selenium.find_element_by_xpath("//input[@type='submit']").submit()
    time.sleep(1)
    assert 'Thank you!' in selenium.page_source, selenium.page_source

    admin_login(selenium, base_url)
    selenium.find_element_by_class_name('icon-form').click()
    assert selenium.current_url == f'{base_url}/admin/forms/'
    contact_forms = selenium.find_elements_by_xpath("//table[@class='listing']//td[@class='title']//a")[0]
    assert contact_forms.text == 'Contact'
    contact_forms.click()

    last_entry = selenium.find_elements_by_xpath("//table[@class='listing']//tbody/tr")[0]
    assert text in last_entry.text
