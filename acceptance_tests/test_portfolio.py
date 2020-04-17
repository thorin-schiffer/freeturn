from pytest import mark


@mark.nondestructive
def test_home(selenium, base_url):
    selenium.get(base_url)
    assert selenium.find_element_by_id('main-avatar')
    assert selenium.find_element_by_id('github-link')
    assert selenium.find_element_by_id('stackoverflow-link')
    assert selenium.find_element_by_id('linkedin-link')
