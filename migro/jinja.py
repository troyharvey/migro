import jinja2
import os

from typing import (
    Optional
)

def env_var(var: str, default: Optional[str] = None) -> str:
    if var in os.environ:
        return os.environ[var]
    elif default is not None:
        return default

def render_jinja_template(template_file, **kwargs):
    env = jinja2.Environment(
        loader = jinja2.FileSystemLoader(searchpath='.'),
        autoescape=jinja2.select_autoescape()
    )
    env.globals['env_var'] = env_var
    template = env.get_template(template_file)
    return template.render(**kwargs)
