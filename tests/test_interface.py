import aiohttp
from pysolarenergy import SolarEnergyInverter
from .data import load_data


async def handle_bytes_response(request):
    """ Faking response """
    response = bytes(123)
    return aiohttp.web.Response(body=response)


async def handle_xml_response(request):
    """ Faking response """
    response = load_data("equipment_data.xml")
    return aiohttp.web.Response(
        content_type="text/xml",
        body=response
    )


async def test_request(aiohttp_client, loop):
    app = aiohttp.web.Application()
    app.router.add_get('/equipment_data.xml', handle_bytes_response)
    client = await aiohttp_client(app)
    inverter = SolarEnergyInverter(session=client)
    response = await inverter._request(endpoint="/equipment_data.xml")
    content = await response.read()
    assert isinstance(content, bytes)
    assert content == bytes(123)


async def test_execute(aiohttp_client, loop):
    app = aiohttp.web.Application()
    app.router.add_get('/equipment_data.xml', handle_xml_response)
    client = await aiohttp_client(app)
    inverter = SolarEnergyInverter(session=client)
    response = await inverter._execute(endpoint="/equipment_data.xml")
    assert response['equipment_data']['Max_DC_POWER'] == '2300'
    response = await inverter._execute(endpoint="/equipment_data.xml", root_element="equipment_data")
    assert response['Max_DC_POWER'] == '2300'


async def test_close_session(aiohttp_client, loop):
    app = aiohttp.web.Application()
    app.router.add_get('/equipment_data.xml', handle_xml_response)
    client = await aiohttp_client(app)
    inverter = SolarEnergyInverter(session=client)
    await client.session.close()
    assert inverter._session.session.closed
