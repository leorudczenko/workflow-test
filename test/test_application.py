from app.main import HelloWorld


def test_toggle_message(hello_world: HelloWorld):
    assert hello_world.window.label_hide is True
    assert hello_world.window.text_label.text() == ""
    hello_world.window.toggle_button.click()
    assert hello_world.window.label_hide is False
    assert hello_world.window.text_label.text() == hello_world.window.default_message
    hello_world.window.toggle_button.click()
    assert hello_world.window.label_hide is True
    assert hello_world.window.text_label.text() == ""
    assert False
