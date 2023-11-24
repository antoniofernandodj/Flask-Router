import quart.flask_patch

from quart import Quart
from router import FlaskRouter
from database import engine
from models import Base
import auth
import logging

logging.basicConfig(level=logging.DEBUG)

app = Quart(__name__)
router = FlaskRouter(app)
router.register_routes(root_name='routes', methods=['GET', 'POST'])
auth.init_app(app)
# Base.metadata.create_all(engine)
app.run()
