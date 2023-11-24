from quart import request
from database import get_session
from models import User

async def index():
    form = await request.form
    session = get_session()
    u = User(username=form['user'], password=form['password'])
    session.add(u)
    session.commit()
    session.close()
    return 'recebido'