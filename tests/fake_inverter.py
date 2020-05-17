from aiohttp import web
import os


def load_data(filename):
    """Load a binary data."""
    path = os.path.join(os.path.dirname(__file__), "data", filename)
    with open(path) as fptr:
        return fptr.read()


async def inverter_response(request):
    resp = web.Response()
    filename = request.path
    resp.body = load_data(filename[1:])
    resp.content_type = 'text/xml'
    return resp


def init():
    app = web.Application()
    app.router.add_get('/equipment_data.xml', inverter_response)
    app.router.add_get('/real_time_data.xml', inverter_response)
    app.router.add_get('/network_data.xml', inverter_response)
    return app


web.run_app(init())
