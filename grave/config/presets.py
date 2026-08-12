"""Pure data — query building lives in the command layer, never here."""

from __future__ import annotations

from grave.models.preset import Preset

PRESETS = [
    Preset(
        name="ancient",
        description="GitHub's earliest repos (2008-2010)",
        keywords=[],
        created_range="2008-01-01..2010-12-31",
        stars_range=">=1",
        category="archaeology",
        sort="stars",
    ),
    Preset(
        name="forgotten",
        description="Old repos with few stars, untouched for 5+ years",
        keywords=[],
        created_range="2008-01-01..2015-12-31",
        stars_range="0..5",
        category="archaeology",
        sort="updated",
    ),
    Preset(
        name="graveyard",
        description="Archived and deprecated projects",
        keywords=["deprecated", "archived", "unmaintained", "abandoned"],
        created_range="2008-01-01..2020-12-31",
        category="archaeology",
        sort="stars",
    ),
    Preset(
        name="one-commit",
        description="Repos with minimal activity, frozen in time",
        keywords=[],
        created_range="2008-01-01..2015-12-31",
        stars_range="0..3",
        category="archaeology",
        sort="updated",
    ),
    Preset(
        name="abandoned-10y",
        description="Repos untouched for 10+ years",
        keywords=[],
        created_range="2008-01-01..2016-12-31",
        pushed="<2016-01-01",
        category="archaeology",
        sort="stars",
    ),
    Preset(
        name="dotfiles-ancient",
        description="The earliest dotfiles and system configs",
        keywords=["dotfiles", "vimrc", "bashrc", "zshrc"],
        created_range="2008-01-01..2012-12-31",
        category="archaeology",
        sort="stars",
    ),
    Preset(
        name="dead-lang",
        description="Projects in legacy/dead programming languages",
        keywords=[],
        language="Fortran",
        created_range="2008-01-01..2018-12-31",
        category="dead-languages",
        sort="stars",
    ),
    Preset(
        name="dead-lang-perl",
        description="Perl relics from the CGI era",
        keywords=[],
        language="Perl",
        created_range="2008-01-01..2015-12-31",
        category="dead-languages",
        sort="stars",
    ),
    Preset(
        name="dead-lang-pascal",
        description="Pascal and Delphi survivors",
        keywords=[],
        language="Pascal",
        created_range="2008-01-01..2018-12-31",
        category="dead-languages",
        sort="stars",
    ),
    Preset(
        name="dead-lang-cobol",
        description="COBOL: the language that won't die",
        keywords=[],
        language="COBOL",
        created_range="2008-01-01..2020-12-31",
        category="dead-languages",
        sort="stars",
    ),
    Preset(
        name="dead-lang-tcl",
        description="Tcl/Tk scripts from a bygone era",
        keywords=[],
        language="Tcl",
        created_range="2008-01-01..2018-12-31",
        category="dead-languages",
        sort="stars",
    ),
    Preset(
        name="dead-lang-smalltalk",
        description="Smalltalk: OOP's grandparent",
        keywords=[],
        language="Smalltalk",
        created_range="2008-01-01..2020-12-31",
        category="dead-languages",
        sort="stars",
    ),
    Preset(
        name="flash-rip",
        description="Flash/ActionScript projects (RIP 2020)",
        keywords=["flash", "swf", "actionscript"],
        language="ActionScript",
        created_range="2008-01-01..2018-12-31",
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
    Preset(
        name="y2k-web",
        description="Y2K-era web tools and relics",
        keywords=["cgi", "guestbook", "webring", "geocities"],
        created_range="2008-01-01..2012-12-31",
        category="eras",
        sort="stars",
    ),
    Preset(
        name="pre-npm",
        description="JavaScript before npm existed (2008-2011)",
        keywords=["jquery", "prototype", "mootools", "scriptaculous"],
        language="JavaScript",
        created_range="2008-01-01..2011-12-31",
        category="eras",
        sort="stars",
    ),
    Preset(
        name="pre-docker",
        description="Infrastructure before containers (Puppet/Chef/Vagrant)",
        keywords=["puppet", "chef", "vagrant", "capistrano", "fabric"],
        created_range="2008-01-01..2013-12-31",
        category="eras",
        sort="stars",
    ),
    Preset(
        name="pre-git",
        description="CVS/SVN migration tools and pre-git relics",
        keywords=["cvs", "svn", "subversion", "mercurial", "bazaar"],
        created_range="2008-01-01..2012-12-31",
        category="eras",
        sort="stars",
    ),
    Preset(
        name="dead-frameworks",
        description="The 2010-2014 frontend graveyard (Backbone, AngularJS 1.x)",
        keywords=["backbone", "angularjs", "knockout", "ember"],
        language="JavaScript",
        created_range="2010-01-01..2014-12-31",
        pushed="<2018-01-01",
        category="eras",
        sort="stars",
    ),
    Preset(
        name="j2me-era",
        description="Pre-smartphone mobile: J2ME, Symbian, WAP",
        keywords=["j2me", "midlet", "symbian"],
        created_range="2008-01-01..2013-12-31",
        category="eras",
        sort="stars",
    ),
    Preset(
        name="homebrew-fossils",
        description="Early macOS/Homebrew era tools",
        keywords=["homebrew", "macports", "fink", "osx"],
        created_range="2008-01-01..2013-12-31",
        category="eras",
        sort="stars",
    ),
    Preset(
        name="digital-utopia",
        description="Digital democracy and virtual world experiments",
        keywords=["democracy", "society", "virtual world", "utopia", "collective"],
        created_range="2008-01-01..2015-12-31",
        category="culture",
        sort="stars",
    ),
    Preset(
        name="cyber-relics",
        description="Early internet culture and cyberspace projects",
        keywords=["cyberspace", "information superhighway", "bulletin board"],
        created_range="2008-01-01..2012-12-31",
        category="culture",
        sort="stars",
    ),
    Preset(
        name="irc-era",
        description="IRC bots, clients, and scripts",
        keywords=["irc", "irc bot", "irc client", "eggdrop"],
        created_range="2008-01-01..2015-12-31",
        category="culture",
        sort="stars",
    ),
    Preset(
        name="myspace-era",
        description="Social network widgets and MySpace-era tools",
        keywords=["myspace", "widget", "social network", "friendster"],
        created_range="2008-01-01..2012-12-31",
        category="culture",
        sort="stars",
    ),
    Preset(
        name="sourceforge-refugees",
        description="Projects migrated from SourceForge",
        keywords=["sourceforge", "migrated", "cvs2git", "svn2git"],
        created_range="2008-01-01..2015-12-31",
        category="culture",
        sort="stars",
    ),
    Preset(
        name="google-code-refugees",
        description="Projects exiled by the Google Code shutdown",
        keywords=["googlecode", "exported from code.google.com"],
        created_range="2008-01-01..2016-12-31",
        category="culture",
        sort="stars",
    ),
    Preset(
        name="dead-social",
        description="Clients and bots for social networks that no longer exist",
        keywords=["vine api", "google plus api", "friendfeed", "orkut"],
        created_range="2008-01-01..2016-12-31",
        pushed="<2020-01-01",
        category="culture",
        sort="stars",
    ),
    Preset(
        name="bbs-era",
        description="Bulletin board systems and BBS door games",
        keywords=["bbs", "bulletin board", "door game", "fidonet", "telnet"],
        created_range="2008-01-01..2015-12-31",
        category="culture",
        sort="stars",
    ),
    Preset(
        name="crypto-og",
        description="Early blockchain and cryptocurrency (2009-2013)",
        keywords=["bitcoin", "blockchain", "cryptocurrency", "mining", "satoshi"],
        created_range="2009-01-01..2013-12-31",
        category="culture",
        sort="stars",
    ),
    Preset(
        name="weird-science",
        description="Experimental science and simulation projects",
        keywords=["experiment", "neural", "genetic", "chaos", "fractal", "simulation"],
        created_range="2008-01-01..2015-12-31",
        category="science",
        sort="stars",
    ),
    Preset(
        name="academic",
        description="Thesis projects and academic research code",
        keywords=["thesis", "dissertation", "phd", "research", "paper"],
        created_range="2008-01-01..2018-12-31",
        category="science",
        sort="stars",
    ),
    Preset(
        name="dead-ai-pre2012",
        description="Pre-AlexNet AI, abandoned by the deep-learning boom",
        keywords=["neural network", "machine learning", "artificial intelligence"],
        created_range="2008-01-01..2012-12-31",
        pushed="<2017-01-01",
        category="science",
        sort="stars",
    ),
]


def list_presets(category: str | None = None) -> list[Preset]:
    """List presets, optionally filtered by category."""
    if category is None:
        return PRESETS
    return [p for p in PRESETS if p.category == category]


def list_categories() -> list[str]:
    """Sorted unique category names."""
    categories = {preset.category for preset in PRESETS}
    return sorted(categories)


def get_preset(name: str) -> Preset | None:
    """Look up a preset by name; None when unknown."""
    for preset in PRESETS:
        if preset.name == name:
            return preset
    return None
