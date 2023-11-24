import quart.flask_patch

from quart import Quart
from flask_router import FlaskRouter
from database import engine
from models import Base
import auth
import logging

logging.basicConfig(level=logging.DEBUG)


app = Quart(__name__)
router = FlaskRouter(app)
router.register_routes(root_name='rotas', methods=['GET', 'POST'])

app.run()