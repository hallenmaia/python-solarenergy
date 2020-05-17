import json
from pysolarenergy import parser
from .data import load_data


def test_parse_xml() -> None:
    data = load_data("unknown_data.xml")
    result = parser.parse_xml_to_json(data)
    assert "unknown_data" in result
    assert result["unknown_data"]["Model"] == "SE-TL2K"
