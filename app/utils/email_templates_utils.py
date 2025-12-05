# app/utils/email_renderer.py
from jinja2 import Environment, FileSystemLoader
import os

template_dir = os.path.join(os.path.dirname(__file__), "../templates/email")
env = Environment(loader=FileSystemLoader(template_dir))

def render_email(template_name: str, context: dict) -> str:
    template = env.get_template(template_name)
    return template.render(context)
