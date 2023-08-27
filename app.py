from quart import Quart
from router import FlaskRouter


app = Quart(__name__)
router = FlaskRouter(app)
router.register_pages(root_name='routes', methods=['GET', 'POST'])
app.run()
