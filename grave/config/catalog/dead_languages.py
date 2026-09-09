from __future__ import annotations

from grave.models.preset import Preset


def _lang(name: str, description: str, language: str, created_end: str, pushed: str) -> Preset:
    return Preset(
        name=name,
        description=description,
        keywords=[],
        language=language,
        created_range=f"2008-01-01..{created_end}",
        pushed=pushed,
        category="dead-languages",
        sort="stars",
    )


PRESETS = [
    _lang(
        "dead-lang",
        "Fortran: still computing, rarely committed",
        "Fortran",
        "2018-12-31",
        "<2020-01-01",
    ),
    _lang("dead-lang-perl", "Perl relics from the CGI era", "Perl", "2015-12-31", "<2018-01-01"),
    _lang("dead-lang-pascal", "Pascal and Delphi survivors", "Pascal", "2018-12-31", "<2020-01-01"),
    _lang(
        "dead-lang-cobol",
        "COBOL: the language that won't die",
        "COBOL",
        "2020-12-31",
        "<2020-01-01",
    ),
    _lang("dead-lang-tcl", "Tcl/Tk scripts from a bygone era", "Tcl", "2018-12-31", "<2020-01-01"),
    _lang(
        "dead-lang-smalltalk",
        "Smalltalk: OOP's grandparent",
        "Smalltalk",
        "2020-12-31",
        "<2020-01-01",
    ),
    Preset(
        name="flash-rip",
        description="Flash/ActionScript projects (RIP 2020)",
        keywords=["flash", "swf", "actionscript"],
        language="ActionScript",
        created_range="2008-01-01..2018-12-31",
        pushed="<2020-01-01",
        category="dead-languages",
        sort="stars",
    ),
    Preset(
        name="dead-lang-coffeescript",
        description="CoffeeScript: the dialect ES6 made obsolete",
        keywords=[],
        language="CoffeeScript",
        created_range="2010-01-01..2016-12-31",
        pushed="<2018-01-01",
        category="dead-languages",
        sort="stars",
    ),
]
