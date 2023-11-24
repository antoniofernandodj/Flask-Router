
from quart import Quart, redirect
from database import engine
from models import User
from sqlalchemy.orm import Session
import flask_login  # type: ignore



def init_app(app: Quart):

    app.config['SECRET_KEY'] = 'eI3tbEhQOs64Asg1qTHaj_rkF3UO06HyxZgL-0OxKGEW9DfxLJzrRMTU'

    login_manager = flask_login.LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        session = Session(engine)
        return session.query(User).filter_by(id=user_id).first()
    

    @login_manager.unauthorized_handler
    def unauthorized():
        return redirect('/login')
