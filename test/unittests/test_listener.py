from unittest.mock import MagicMock

import pytest

from ovos_ui_enclosure_protocol import EnclosureProtocolListener


class FakeBus:
    """Minimal bus recording on/remove registrations and able to emit."""

    def __init__(self):
        self.handlers = {}      # msg_type -> list of callbacks
        self.on_calls = []      # (msg_type, callback)
        self.remove_calls = []  # (msg_type, callback)

    def on(self, msg_type, callback):
        self.on_calls.append((msg_type, callback))
        self.handlers.setdefault(msg_type, []).append(callback)

    def remove(self, msg_type, callback):
        self.remove_calls.append((msg_type, callback))
        if msg_type in self.handlers and callback in self.handlers[msg_type]:
            self.handlers[msg_type].remove(callback)

    def emit_event(self, msg_type, message=None):
        for cb in list(self.handlers.get(msg_type, [])):
            cb(message)


class Listener(EnclosureProtocolListener):
    def __init__(self, bus):
        self.bus = bus


# every enclosure.* event the protocol owns on the listener side
EXPECTED_EVENTS = [
    "enclosure.notify.no_internet",
    "enclosure.reset",
    "enclosure.system.reset",
    "enclosure.system.mute",
    "enclosure.system.unmute",
    "enclosure.system.blink",
    "enclosure.eyes.on",
    "enclosure.eyes.off",
    "enclosure.eyes.blink",
    "enclosure.eyes.narrow",
    "enclosure.eyes.look",
    "enclosure.eyes.color",
    "enclosure.eyes.level",
    "enclosure.eyes.volume",
    "enclosure.eyes.spin",
    "enclosure.eyes.timedspin",
    "enclosure.eyes.reset",
    "enclosure.eyes.setpixel",
    "enclosure.eyes.fill",
    "enclosure.mouth.events.activate",
    "enclosure.mouth.events.deactivate",
    "enclosure.mouth.talk",
    "enclosure.mouth.think",
    "enclosure.mouth.listen",
    "enclosure.mouth.smile",
    "enclosure.mouth.viseme",
    "enclosure.mouth.viseme_list",
    "enclosure.mouth.reset",
    "enclosure.mouth.text",
    "enclosure.mouth.display",
    "enclosure.weather.display",
]


@pytest.fixture
def bus():
    return FakeBus()


@pytest.fixture
def listener(bus):
    return Listener(bus)


def test_register_wires_all_events(listener, bus):
    listener.register_enclosure_namespace()
    registered = {mt for mt, _ in bus.on_calls}
    for ev in EXPECTED_EVENTS:
        assert ev in registered, f"{ev} not registered"


def test_register_count_matches(listener, bus):
    listener.register_enclosure_namespace()
    assert len(bus.on_calls) == len(EXPECTED_EVENTS)


def test_shutdown_removes_all_events(listener, bus):
    listener.register_enclosure_namespace()
    listener.shutdown_enclosure_namespace()
    removed = {mt for mt, _ in bus.remove_calls}
    for ev in EXPECTED_EVENTS:
        assert ev in removed, f"{ev} not removed"
    # nothing left subscribed
    assert all(len(cbs) == 0 for cbs in bus.handlers.values())


@pytest.mark.parametrize("event,handler_name", [
    ("enclosure.reset", "on_reset"),
    ("enclosure.notify.no_internet", "on_no_internet"),
    ("enclosure.system.reset", "on_system_reset"),
    ("enclosure.system.mute", "on_system_mute"),
    ("enclosure.system.unmute", "on_system_unmute"),
    ("enclosure.system.blink", "on_system_blink"),
    ("enclosure.eyes.on", "on_eyes_on"),
    ("enclosure.eyes.off", "on_eyes_off"),
    ("enclosure.eyes.blink", "on_eyes_blink"),
    ("enclosure.eyes.narrow", "on_eyes_narrow"),
    ("enclosure.eyes.look", "on_eyes_look"),
    ("enclosure.eyes.color", "on_eyes_color"),
    ("enclosure.eyes.level", "on_eyes_brightness"),
    ("enclosure.eyes.volume", "on_eyes_volume"),
    ("enclosure.eyes.spin", "on_eyes_spin"),
    ("enclosure.eyes.timedspin", "on_eyes_timed_spin"),
    ("enclosure.eyes.reset", "on_eyes_reset"),
    ("enclosure.eyes.setpixel", "on_eyes_set_pixel"),
    ("enclosure.eyes.fill", "on_eyes_fill"),
    ("enclosure.mouth.reset", "on_display_reset"),
    ("enclosure.mouth.text", "on_text"),
    ("enclosure.mouth.display", "on_display"),
    ("enclosure.weather.display", "on_weather_display"),
])
def test_event_routes_to_handler(bus, event, handler_name):
    """Emitting an event calls the named overridable handler."""
    listener = Listener(bus)
    listener.register_enclosure_namespace()
    called = {}

    def fake(message=None):
        called["hit"] = message

    setattr(listener, handler_name, fake)
    # re-register so the patched handler is wired for directly-bound events
    bus.handlers.clear()
    bus.on_calls.clear()
    listener.register_enclosure_namespace()

    sentinel = object()
    bus.emit_event(event, sentinel)
    assert called.get("hit") is sentinel


def test_default_handlers_are_noops(listener):
    """All default handlers accept a message and return None."""
    handler_names = [
        "on_reset", "on_no_internet", "on_system_reset", "on_system_mute",
        "on_system_unmute", "on_system_blink", "on_eyes_on", "on_eyes_off",
        "on_eyes_fill", "on_eyes_blink", "on_eyes_narrow", "on_eyes_look",
        "on_eyes_color", "on_eyes_brightness", "on_eyes_reset",
        "on_eyes_timed_spin", "on_eyes_volume", "on_eyes_spin",
        "on_eyes_set_pixel", "on_display_reset", "on_talk", "on_think",
        "on_listen", "on_smile", "on_viseme", "on_viseme_list", "on_text",
        "on_display", "on_weather_display",
    ]
    for name in handler_names:
        assert getattr(listener, name)(MagicMock()) is None


def test_mouth_events_gating_default_off(bus):
    """Mouth animation events are suppressed until activated."""
    listener = Listener(bus)
    listener.register_enclosure_namespace()
    hits = []
    listener.on_talk = lambda m=None: hits.append("talk")
    listener.on_think = lambda m=None: hits.append("think")

    assert listener.mouth_events_active is False
    bus.emit_event("enclosure.mouth.talk")
    bus.emit_event("enclosure.mouth.think")
    assert hits == []


def test_mouth_events_gating_activate(bus):
    listener = Listener(bus)
    listener.register_enclosure_namespace()
    hits = []
    listener.on_talk = lambda m=None: hits.append("talk")

    bus.emit_event("enclosure.mouth.events.activate")
    assert listener.mouth_events_active is True
    bus.emit_event("enclosure.mouth.talk")
    assert hits == ["talk"]

    bus.emit_event("enclosure.mouth.events.deactivate")
    assert listener.mouth_events_active is False
    bus.emit_event("enclosure.mouth.talk")
    assert hits == ["talk"]  # no new hit


def test_all_mouth_animation_events_gated(bus):
    listener = Listener(bus)
    listener.register_enclosure_namespace()
    calls = []
    for name in ("on_talk", "on_think", "on_listen", "on_smile",
                 "on_viseme", "on_viseme_list"):
        setattr(listener, name, (lambda n: (lambda m=None: calls.append(n)))(name))

    events = ["enclosure.mouth.talk", "enclosure.mouth.think",
              "enclosure.mouth.listen", "enclosure.mouth.smile",
              "enclosure.mouth.viseme", "enclosure.mouth.viseme_list"]

    # gated off
    for ev in events:
        bus.emit_event(ev)
    assert calls == []

    # gated on
    listener._activate_mouth_events()
    for ev in events:
        bus.emit_event(ev)
    assert calls == ["on_talk", "on_think", "on_listen", "on_smile",
                     "on_viseme", "on_viseme_list"]


def test_subclass_overrides_handler(bus):
    """A hardware subclass overriding a handler receives the event."""
    received = []

    class HardwarePlugin(EnclosureProtocolListener):
        def __init__(self, bus):
            self.bus = bus

        def on_eyes_color(self, message=None):
            received.append(message)

    plugin = HardwarePlugin(bus)
    plugin.register_enclosure_namespace()
    msg = MagicMock()
    bus.emit_event("enclosure.eyes.color", msg)
    assert received == [msg]
