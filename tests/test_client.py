import pytest
import aiohttp
import asyncio
import pysolarenergy
from .data import load_data


async def handle_response(request):
    """ Faking response """
    resp = aiohttp.web.Response()
    filename = request.path
    resp.body = load_data(filename[1:])
    resp.content_type = 'text/xml'
    return resp


async def test_get_info(aiohttp_client, loop):
    app = aiohttp.web.Application()
    app.router.add_get('/equipment_data.xml', handle_response)
    client = await aiohttp_client(app)
    inverter = pysolarenergy.SolarEnergyInverter(session=client)
    response = await inverter.get_info()
    assert response['Product_Code'] == 'SU02KSTL1BR6ED2103'


async def test_get_data(aiohttp_client, loop):
    app = aiohttp.web.Application()
    app.router.add_get('/real_time_data.xml', handle_response)
    client = await aiohttp_client(app)
    inverter = pysolarenergy.SolarEnergyInverter(session=client)
    response = await inverter.get_data()
    assert response['v-bus'] == '360.2'


async def test_get_network(aiohttp_client, loop):
    app = aiohttp.web.Application()
    app.router.add_get('/network_data.xml', handle_response)
    client = await aiohttp_client(app)
    inverter = pysolarenergy.SolarEnergyInverter(session=client)
    response = await inverter.get_network()
    assert response['MAC_Add'] == 'E0-02-02-02-16-90'


# SolarEnergyConnectionError #
#  SolarEnergyTimeoutError #
async def test_request_timeout_error(aiohttp_client, loop):
    """ Test for timeout """
    # Faking a timeout by sleeping
    async def handle_timeout(request):
        await asyncio.sleep(4)
        return aiohttp.web.Response(body="Timeout!")

    app = aiohttp.web.Application()
    app.router.add_get('/equipment_data.xml', handle_timeout)
    client = await aiohttp_client(app)
    inverter = pysolarenergy.SolarEnergyInverter(session=client, request_timeout=2)
    with pytest.raises(pysolarenergy.SolarEnergyTimeoutError):
        await inverter.get_info()
    with pytest.raises(pysolarenergy.SolarEnergyConnectionError):
        await inverter.get_info()


#  SolarEnergyClientError #
async def test_invalid_url_error(aiohttp_client, loop):
    """ Test for 404 """
    # Faking a 404
    async def handle_404(request):
        return aiohttp.web.Response(status=404)

    app = aiohttp.web.Application()
    app.router.add_get('/equipment_data', handle_404)
    client = await aiohttp_client(app)
    inverter = pysolarenergy.SolarEnergyInverter(session=client)
    with pytest.raises(pysolarenergy.SolarEnergyClientError):
        await inverter.get_info()


#  SolarEnergyClientError #
async def test_session_closed_error(aiohttp_client, loop):
    app = aiohttp.web.Application()
    app.router.add_get('/equipment_data.xml', handle_response)
    client = await aiohttp_client(app)
    inverter = pysolarenergy.SolarEnergyInverter(session=client)
    await client.session.close()
    with pytest.raises(pysolarenergy.SolarEnergyClientError):
        await inverter.get_info()


# SolarEnergyResponseError #
#  SolarEnergyParseError #
async def test_invalid_parse_error(aiohttp_client, loop):
    """ Test for xml error """
    # Faking invalid xml
    async def handle_xml_error(request):
        response = load_data("invalid_data.xml")
        return aiohttp.web.Response(
            content_type="text/xml",
            body=response
        )

    app = aiohttp.web.Application()
    app.router.add_get('/equipment_data.xml', handle_xml_error)
    client = await aiohttp_client(app)
    inverter = pysolarenergy.SolarEnergyInverter(session=client)
    with pytest.raises(pysolarenergy.SolarEnergyParseError):
        await inverter.get_info()


#  SolarEnergyContentTypeError #
async def test_content_type_error(aiohttp_client, loop):
    """ Test for xml error """
    async def handle_xml_error(request):
        response = load_data("equipment_data.xml")
        return aiohttp.web.Response(
            content_type="text/plain",
            body=response
        )

    app = aiohttp.web.Application()
    app.router.add_get('/equipment_data.xml', handle_xml_error)
    client = await aiohttp_client(app)
    inverter = pysolarenergy.SolarEnergyInverter(session=client)
    with pytest.raises(pysolarenergy.SolarEnergyContentTypeError):
        await inverter.get_info()


#  SolarEnergyAttributeError #
async def test_invalid_attribute_error(aiohttp_client, loop):
    """ Test for xml error """
    async def handle_xml_error(request):
        response = load_data("unknown_data.xml")
        return aiohttp.web.Response(
            content_type="text/xml",
            body=response
        )

    app = aiohttp.web.Application()
    app.router.add_get('/equipment_data.xml', handle_xml_error)
    client = await aiohttp_client(app)
    inverter = pysolarenergy.SolarEnergyInverter(session=client)
    with pytest.raises(pysolarenergy.SolarEnergyAttributeError):
        await inverter.get_info()
