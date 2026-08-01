from unittest.mock import MagicMock

import pytest

from ovos_spec_tools import SpecMessage

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


# every topic the listener owns (enclosure.* + the activate/deactivate toggles)
ENCLOSURE_TOPICS = {t for t, _ in EnclosureProtocolListener.ENCLOSURE_EVENTS.values()}
ENCLOSURE_TOPICS |= {"enclosure.mouth.events.activate",
                     "enclosure.mouth.events.deactivate"}
CORE_TOPICS = {t for t, _ in EnclosureProtocolListener.CORE_EVENTS.values()}


@pytest.fixture
def bus():
    return FakeBus()


def test_instantiation_with_bus_wires_everything(bus):
    EnclosureProtocolListener(bus=bus)
    wired = {mt for mt, _ in bus.on_calls}
    assert ENCLOSURE_TOPICS <= wired
    assert CORE_TOPICS <= wired


def test_no_bus_defers_wiring():
    listener = EnclosureProtocolListener(bus=None)
    assert listener.bus is None
    bus = FakeBus()
    listener.set_bus(bus)
    wired = {mt for mt, _ in bus.on_calls}
    assert ENCLOSURE_TOPICS <= wired and CORE_TOPICS <= wired


def test_callbacks_in_constructor_fire(bus):
    hits = {}
    EnclosureProtocolListener(
        bus=bus,
        on_eyes_color=lambda m=None: hits.setdefault("eyes_color", m),
        on_record_begin=lambda m=None: hits.setdefault("record_begin", m),
    )
    sentinel = object()
    bus.emit_event("enclosure.eyes.color", sentinel)
    bus.emit_event(SpecMessage.LISTENER_RECORD_STARTED, sentinel)
    assert hits == {"eyes_color": sentinel, "record_begin": sentinel}


def test_set_callback_registers_late(bus):
    listener = EnclosureProtocolListener(bus=bus)
    seen = []
    listener.set_callback("on_text", lambda m=None: seen.append(m))
    bus.emit_event("enclosure.mouth.text", "hi")
    assert seen == ["hi"]


def test_set_callback_rejects_unknown_name(bus):
    listener = EnclosureProtocolListener(bus=bus)
    with pytest.raises(KeyError):
        listener.set_callback("on_bogus", lambda m=None: None)


def test_event_without_callback_is_ignored(bus):
    # no callbacks registered: emitting must not raise
    EnclosureProtocolListener(bus=bus)
    bus.emit_event("enclosure.eyes.on")
    bus.emit_event(SpecMessage.SPEAK)


@pytest.mark.parametrize("name,topic", [
    (n, t) for n, (t, _) in {**EnclosureProtocolListener.ENCLOSURE_EVENTS,
                             **EnclosureProtocolListener.CORE_EVENTS}.items()
])
def test_every_event_routes_to_its_callback(bus, name, topic):
    gated = (name in EnclosureProtocolListener.ENCLOSURE_EVENTS
             and EnclosureProtocolListener.ENCLOSURE_EVENTS[name][1])
    seen = []
    listener = EnclosureProtocolListener(bus=bus)
    listener.set_callback(name, lambda m=None: seen.append(m))
    if gated:
        listener.activate_mouth_events()
    sentinel = object()
    bus.emit_event(topic, sentinel)
    assert seen == [sentinel]


def test_mouth_animation_gating(bus):
    hits = []
    listener = EnclosureProtocolListener(
        bus=bus,
        on_talk=lambda m=None: hits.append("talk"),
        on_think=lambda m=None: hits.append("think"),
    )
    assert listener.mouth_events_active is False
    bus.emit_event("enclosure.mouth.talk")
    bus.emit_event("enclosure.mouth.think")
    assert hits == []  # gated off

    bus.emit_event("enclosure.mouth.events.activate")
    assert listener.mouth_events_active is True
    bus.emit_event("enclosure.mouth.talk")
    assert hits == ["talk"]

    bus.emit_event("enclosure.mouth.events.deactivate")
    assert listener.mouth_events_active is False
    bus.emit_event("enclosure.mouth.talk")
    assert hits == ["talk"]  # no new hit


def test_non_gated_mouth_events_always_fire(bus):
    seen = []
    EnclosureProtocolListener(bus=bus, on_text=lambda m=None: seen.append(m))
    # text/display/reset are not gated by mouth_events
    bus.emit_event("enclosure.mouth.text", "x")
    assert seen == ["x"]


def test_shutdown_removes_all_subscriptions(bus):
    listener = EnclosureProtocolListener(bus=bus)
    listener.shutdown()
    removed = {mt for mt, _ in bus.remove_calls}
    assert ENCLOSURE_TOPICS <= removed
    assert CORE_TOPICS <= removed
    assert all(len(cbs) == 0 for cbs in bus.handlers.values())


def test_dispatchers_are_stable_across_register_and_shutdown(bus):
    """register and shutdown must use the SAME callable so remove matches on."""
    listener = EnclosureProtocolListener(bus=bus)
    on_by_topic = {mt: cb for mt, cb in bus.on_calls}
    listener.shutdown_enclosure_namespace()
    listener.shutdown_core_events()
    remove_by_topic = {mt: cb for mt, cb in bus.remove_calls}
    # bus.remove matches by equality; dispatcher closures are identical objects,
    # the activate/deactivate bound methods compare equal (same instance+func).
    for topic in CORE_TOPICS | ENCLOSURE_TOPICS:
        assert on_by_topic[topic] == remove_by_topic[topic]
