from quart import make_response

async def index():
    response = await make_response('''
    <clientes>
        <cliente>
            <id>1</id>
            <nome>TreinaWeb Cursos</nome>
            <idade>10</idade>
        </cliente>
    </clientes>
    ''')

    response.content_type = 'application/xml'

    return response