from flask_login import logout_user  # type: ignore
from quart import redirect


def index():
    logout_user()
    return redirect('/login')