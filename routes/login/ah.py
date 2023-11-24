from quart import render_template
from flask_login import login_required  # type: ignore


ola = 'mundo'

def index():
    return 'ola mundo'
