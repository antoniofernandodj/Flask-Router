from quart import render_template
from flask_login import login_required  # type: ignore


@login_required
async def index():
    return await render_template('index.html')
