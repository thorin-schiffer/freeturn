from pytest import fixture

WINDOW_HEIGHT = 1080
WINDOW_WIDTH = 1920


@fixture(autouse=True)
def prepare_window(selenium):
    selenium.set_window_size(WINDOW_WIDTH, WINDOW_HEIGHT)
