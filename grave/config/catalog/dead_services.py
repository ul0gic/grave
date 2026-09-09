from __future__ import annotations

from dataclasses import replace

from grave.models.preset import Preset


def _service(
    name: str, description: str, keywords: list[str], created_range: str, pushed: str
) -> Preset:
    return Preset(
        name=name,
        description=description,
        keywords=keywords,
        created_range=created_range,
        pushed=pushed,
        category="dead-services",
        sort="stars",
    )


PRESETS = [
    _service(
        "google-reader",
        "Clients and clones built for Google Reader",
        ["google reader"],
        "2008-01-01..2013-12-31",
        "<2015-01-01",
    ),
    _service(
        "google-wave",
        "Gadgets and robots for Google Wave",
        ["google wave", "wave gadget", "wave robot"],
        "2009-01-01..2011-12-31",
        "<2013-01-01",
    ),
    _service(
        "parse-refugees",
        "Apps built on the Parse.com backend",
        ["parse.com", "parse cloud code"],
        "2011-01-01..2016-12-31",
        "<2018-01-01",
    ),
    _service(
        "checkin-wars",
        "Foursquare and Gowalla check-in apps",
        ["foursquare", "gowalla", "checkin"],
        "2009-01-01..2013-12-31",
        "<2016-01-01",
    ),
    _service(
        "yahoo-graveyard",
        "Yahoo Pipes, Delicious, and YQL mashups",
        ["yahoo pipes", "delicious", "yql"],
        "2008-01-01..2013-12-31",
        "<2016-01-01",
    ),
    _service(
        "app-net",
        "Clients for App.net, the paid Twitter alternative",
        ["app.net", "alpha api"],
        "2012-01-01..2014-12-31",
        "<2017-01-01",
    ),
    replace(
        _service(
            "flash-games",
            "Browser games from the Flash era",
            ["flash game", "flixel", "flashpunk"],
            "2008-01-01..2015-12-31",
            "<2018-01-01",
        ),
        language="ActionScript",
    ),
]
