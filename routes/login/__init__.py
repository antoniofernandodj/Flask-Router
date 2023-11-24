from quart import render_template, request, redirect, url_for
from flask_login import login_required, login_user  # type: ignore
from database import get_session
from models import User




async def index():

    if request.method == 'POST':
        form = await request.form

        session = get_session()
        user = session.query(User).filter_by(username=form['username']).first()
        if user:
            login_user(user)
            return redirect(url_for('index'))
        
        else:
            return redirect(url_for('login.index'))

    elif request.method == 'GET':

        return await render_template('login.html')

    return ''
