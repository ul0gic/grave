"""Named technology-era date ranges for the ``--era`` flag."""

from __future__ import annotations

# Era mapping for --era flag
ERAS = {
    "y2k": ("1999-01-01", "2003-12-31"),
    "dotcom": ("1997-01-01", "2001-12-31"),
    "web2.0": ("2004-01-01", "2009-12-31"),
    "early-github": ("2008-01-01", "2011-12-31"),
    "pre-mobile": ("2007-01-01", "2010-12-31"),
}
