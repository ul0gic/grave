"""Ideas that arrived before the tech did — the raw material for a modern rethink."""

from __future__ import annotations

from dataclasses import replace

from grave.models.preset import Preset


def _idea(name: str, description: str, keywords: list[str], until: str, dead: str) -> Preset:
    return Preset(
        name=name,
        description=description,
        keywords=keywords,
        created_range=f"2008-01-01..{until}",
        pushed=dead,
        category="ahead-of-time",
        sort="stars",
    )


PRESETS = [
    _idea(
        "proto-smartwatch",
        "Smartwatches built years before Apple's",
        ["smartwatch", "smart watch", "pebble", "metawatch"],
        "2013-12-31",
        "<2016-01-01",
    ),
    _idea(
        "vr-before-oculus",
        "Virtual reality before the Oculus Kickstarter",
        ["virtual reality", "head mounted display", "stereoscopic"],
        "2012-12-31",
        "<2015-01-01",
    ),
    replace(
        _idea(
            "ar-before-arkit",
            "Augmented reality on phones that could barely run it",
            ["augmented reality"],
            "2012-12-31",
            "<2016-01-01",
        ),
        match="name,description",
    ),
    _idea(
        "voice-before-alexa",
        "Voice assistants before Alexa and Siri got good",
        ["voice assistant", "speech recognition", "jarvis"],
        "2013-12-31",
        "<2016-01-01",
    ),
    _idea(
        "chatbots-before-llm",
        "Chatbots from the AIML era, before language models",
        ["chatbot", "aiml", "conversational agent"],
        "2014-12-31",
        "<2017-01-01",
    ),
    _idea(
        "smart-home-early",
        "Home automation before HomeKit and Nest",
        ["home automation", "smart home", "x10"],
        "2013-12-31",
        "<2016-01-01",
    ),
    _idea(
        "self-driving-hobby",
        "Hobbyist self-driving cars before the industry caught up",
        ["self driving", "autonomous car", "autonomous vehicle"],
        "2014-12-31",
        "<2017-01-01",
    ),
    _idea(
        "diy-drones",
        "Garage-built quadcopters before DJI made them a product",
        ["quadcopter", "multicopter", "ardupilot"],
        "2013-12-31",
        "<2016-01-01",
    ),
    _idea(
        "brain-interface",
        "Brain-computer interfaces on consumer EEG headsets",
        ["brain computer interface", "eeg", "neurofeedback"],
        "2014-12-31",
        "<2017-01-01",
    ),
    _idea(
        "gesture-control",
        "Gesture and hand tracking from the Kinect hacking wave",
        ["gesture recognition", "hand tracking", "kinect"],
        "2013-12-31",
        "<2016-01-01",
    ),
    _idea(
        "wearables-early",
        "Wearables and e-textiles before the category existed",
        ["wearable", "e-textile", "lilypad"],
        "2013-12-31",
        "<2016-01-01",
    ),
    _idea(
        "decentralized-social",
        "Federated and P2P social networks a decade before Mastodon",
        ["diaspora", "federated", "distributed social", "p2p social"],
        "2013-12-31",
        "<2016-01-01",
    ),
    _idea(
        "mesh-networks",
        "Community mesh networks and darknets",
        ["mesh network", "meshnet", "darknet"],
        "2014-12-31",
        "<2017-01-01",
    ),
    _idea(
        "3d-printing-early",
        "RepRap-era 3D printing tooling",
        ["3d printer", "reprap", "gcode"],
        "2012-12-31",
        "<2015-01-01",
    ),
    _idea(
        "iot-before-iot",
        "Connected sensors before anyone said Internet of Things",
        ["internet of things", "sensor network", "arduino ethernet"],
        "2013-12-31",
        "<2016-01-01",
    ),
    _idea(
        "realtime-collab",
        "Realtime collaborative editing before it was table stakes",
        ["operational transformation", "collaborative editor", "realtime collaboration"],
        "2013-12-31",
        "<2016-01-01",
    ),
    _idea(
        "semantic-web",
        "The semantic web: RDF, ontologies, linked data",
        ["semantic web", "rdf", "ontology", "linked data"],
        "2013-12-31",
        "<2016-01-01",
    ),
    _idea(
        "quantified-self",
        "Lifelogging and self-tracking before fitness trackers",
        ["quantified self", "lifelogging", "self tracking"],
        "2014-12-31",
        "<2017-01-01",
    ),
    _idea(
        "e-paper",
        "E-ink hacks and e-paper displays",
        ["e-ink", "epaper", "kindle hack"],
        "2014-12-31",
        "<2017-01-01",
    ),
    replace(
        _idea(
            "kickstarter-corpses",
            "Crowdfunded projects whose code outlived the campaign",
            ["kickstarter", "indiegogo"],
            "2015-12-31",
            "<2018-01-01",
        ),
        created_range="2009-01-01..2015-12-31",
        match="description",
    ),
]
