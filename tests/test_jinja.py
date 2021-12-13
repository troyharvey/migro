from migro import jinja


def test_env_var():
    assert "foo" == jinja.env_var("FOO")


def test_env_var_default():
    assert "bar" == jinja.env_var("BAR", "bar")


def test_render_jinja_template_with_env_var():
    assert "password: verySECRETpassword" in jinja.render_jinja_template("profiles.yml")
