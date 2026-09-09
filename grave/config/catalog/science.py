from __future__ import annotations

from grave.models.preset import Preset

PRESETS = [
    Preset(
        name="weird-science",
        description="Experimental science and simulation projects",
        keywords=["experiment", "neural", "genetic", "chaos", "fractal", "simulation"],
        created_range="2008-01-01..2015-12-31",
        pushed="<2018-01-01",
        category="science",
        sort="stars",
    ),
    Preset(
        name="academic",
        description="Thesis projects and academic research code",
        keywords=["thesis", "dissertation", "phd", "research", "paper"],
        created_range="2008-01-01..2018-12-31",
        pushed="<2020-01-01",
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
