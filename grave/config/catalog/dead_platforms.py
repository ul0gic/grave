from __future__ import annotations

from grave.models.preset import Preset


def _platform(
    name: str, description: str, keywords: list[str], created_range: str, pushed: str
) -> Preset:
    return Preset(
        name=name,
        description=description,
        keywords=keywords,
        created_range=created_range,
        pushed=pushed,
        category="dead-platforms",
        sort="stars",
    )


PRESETS = [
    _platform(
        "windows-phone",
        "Windows Phone, Silverlight, and XNA apps",
        ["windows phone", "silverlight", "xna"],
        "2010-01-01..2015-12-31",
        "<2018-01-01",
    ),
    _platform(
        "blackberry",
        "BlackBerry and BB10 apps",
        ["blackberry", "bb10", "webworks"],
        "2008-01-01..2014-12-31",
        "<2017-01-01",
    ),
    _platform(
        "palm-webos",
        "Palm Pre and TouchPad webOS apps",
        ["webos", "palm pre", "touchpad"],
        "2009-01-01..2013-12-31",
        "<2015-01-01",
    ),
    _platform(
        "google-glass",
        "Glassware from the Google Glass Explorer year",
        ["google glass", "glassware"],
        "2013-01-01..2015-12-31",
        "<2017-01-01",
    ),
    _platform(
        "firefox-os",
        "Firefox OS and Boot2Gecko apps",
        ["firefox os", "firefoxos", "boot2gecko"],
        "2012-01-01..2016-12-31",
        "<2018-01-01",
    ),
    _platform(
        "chrome-apps",
        "Packaged Chrome Apps, retired in 2020",
        ["chrome app", "packaged app"],
        "2012-01-01..2017-12-31",
        "<2020-01-01",
    ),
    _platform(
        "kinect-hacks",
        "The 2010-2014 Kinect hacking scene",
        ["kinect", "openni", "libfreenect"],
        "2010-01-01..2014-12-31",
        "<2016-01-01",
    ),
]
