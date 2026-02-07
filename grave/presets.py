"""Search preset definitions and management.

This module defines curated search presets for discovering old, weird,
and forgotten GitHub repositories. Each preset contains search parameters
that generate specific GitHub search queries.
"""

from dataclasses import dataclass

from grave.api import build_search_query


@dataclass
class Preset:
    """A curated search preset for GitHub repository discovery.

    Attributes:
        name: Unique identifier for the preset
        description: Human-readable description of what this preset finds
        keywords: Keywords to include in the search query
        created_range: Date range for repository creation (e.g., '2000..2010')
        language: Programming language filter (optional)
        stars_range: Star count filter (e.g., '>100', '10..50')
        pushed: Last push date filter (e.g., '<2015-01-01')
        category: Category grouping for the preset
        sort: Sort order for results ('stars', 'forks', 'updated')
    """

    name: str
    description: str
    keywords: list[str]
    created_range: str | None = None
    language: str | None = None
    stars_range: str | None = None
    pushed: str | None = None
    category: str = "general"
    sort: str = "stars"

    def build_query(self) -> str:
        """Convert this preset into a GitHub search query string.

        Returns:
            Valid GitHub search query string
        """
        return build_search_query(
            keywords=self.keywords if self.keywords else None,
            created_range=self.created_range,
            language=self.language,
            stars_range=self.stars_range,
            pushed=self.pushed,
        )


# Curated search presets for discovering forgotten GitHub repositories
PRESETS = [
    # ARCHAEOLOGY - Digging up old stuff
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
    # DEAD-LANGUAGES - Legacy and dead programming languages
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
    # ERAS - Technology time periods
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
        name="homebrew-fossils",
        description="Early macOS/Homebrew era tools",
        keywords=["homebrew", "macports", "fink", "osx"],
        created_range="2008-01-01..2013-12-31",
        category="eras",
        sort="stars",
    ),
    # CULTURE - Internet culture and communities
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
    # SCIENCE - Research and experimental projects
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
]


def list_presets(category: str | None = None) -> list[Preset]:
    """Get list of all available search presets.

    Args:
        category: Optional category filter to return only presets in that category

    Returns:
        List of Preset objects, optionally filtered by category
    """
    if category is None:
        return PRESETS
    return [p for p in PRESETS if p.category == category]


def list_categories() -> list[str]:
    """Get sorted list of unique category names.

    Returns:
        Sorted list of category names
    """
    categories = {preset.category for preset in PRESETS}
    return sorted(categories)


def get_preset(name: str) -> Preset | None:
    """Get a preset by name.

    Args:
        name: Preset name identifier

    Returns:
        Preset object if found, None otherwise
    """
    for preset in PRESETS:
        if preset.name == name:
            return preset
    return None
