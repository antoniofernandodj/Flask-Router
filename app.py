from quart import Quart
from router import FlaskRouting


app = Quart(__name__)
router = FlaskRouting(app)
router.register_pages(root_name='routes', methods=['GET', 'POST'])
app.run()
