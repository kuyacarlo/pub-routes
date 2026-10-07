from pathlib import Path
import importlib.util

spec = importlib.util.spec_from_file_location("pub_routes_parser", Path(__file__).resolve().parents[1] / "03.py")
parser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parser)


def test_puv_parser_skips_totals_and_status_rows():
    rows = [
        ["Land Transportation Franchising Regulatory Board", None],
        ["PUJ Routes", "Route Name"],
        ["With Approved LPTRP", None],
        ["Above 60% consolidation", None],
        ["1", "CITY A - CITY B"],
        ["Count", "Route Name"],
    ]

    df = parser.PUVParser("ncr").get_dataframe(rows)

    assert df.to_dict("records") == [
        {
            "region": "ncr",
            "transpo_type": "PUJ",
            "route_name": "CITY A - CITY B",
            "route_status": "approved_lptrp",
            "is_consolidated": True,
            "is_above_consolidation_threshold": True,
        }
    ]


def test_get_region_name_supports_parenthesized_region_names():
    assert parser.get_region_name("Region III Routes (Central Luzon)") == "central_luzon"
