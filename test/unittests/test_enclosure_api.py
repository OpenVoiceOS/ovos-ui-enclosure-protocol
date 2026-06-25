from unittest.mock import MagicMock

import pytest

from ovos_ui_enclosure_protocol import EnclosureAPI


@pytest.fixture
def bus():
    return MagicMock()


@pytest.fixture
def api(bus):
    return EnclosureAPI(bus=bus, skill_id="test.skill")


def _emitted(bus):
    """Return the single Message passed to bus.emit on the last call."""
    assert bus.emit.call_count == 1
    return bus.emit.call_args[0][0]


def _assert_msg(bus, msg_type, data=None):
    msg = _emitted(bus)
    assert msg.msg_type == msg_type
    if data is not None:
        assert msg.data == data
    return msg


def test_constructor_defaults():
    api = EnclosureAPI()
    assert api.bus is None
    assert api.skill_id == ""


def test_set_bus_and_id():
    api = EnclosureAPI()
    bus = MagicMock()
    api.set_bus(bus)
    api.set_id("foo.skill")
    assert api.bus is bus
    assert api.skill_id == "foo.skill"


def test_source_message_context(api):
    """When no inbound message exists, a new one is built targeting the enclosure."""
    msg = api._get_source_message()
    assert msg.context["destination"] == ["enclosure"]
    assert msg.context["skill_id"] == "test.skill"


def test_register_uses_self_skill_id(api, bus):
    api.register()
    _assert_msg(bus, "enclosure.active_skill", {"skill_id": "test.skill"})


def test_register_explicit_skill_id(api, bus):
    api.register("other.skill")
    _assert_msg(bus, "enclosure.active_skill", {"skill_id": "other.skill"})


def test_reset(api, bus):
    api.reset()
    _assert_msg(bus, "enclosure.reset", {})


def test_system_reset(api, bus):
    api.system_reset()
    _assert_msg(bus, "enclosure.system.reset", {})


def test_system_mute(api, bus):
    api.system_mute()
    _assert_msg(bus, "enclosure.system.mute", {})


def test_system_unmute(api, bus):
    api.system_unmute()
    _assert_msg(bus, "enclosure.system.unmute", {})


def test_system_blink(api, bus):
    api.system_blink(3)
    _assert_msg(bus, "enclosure.system.blink", {"times": 3})


def test_eyes_on(api, bus):
    api.eyes_on()
    _assert_msg(bus, "enclosure.eyes.on", {})


def test_eyes_off(api, bus):
    api.eyes_off()
    _assert_msg(bus, "enclosure.eyes.off", {})


def test_eyes_blink(api, bus):
    api.eyes_blink("b")
    _assert_msg(bus, "enclosure.eyes.blink", {"side": "b"})


def test_eyes_narrow(api, bus):
    api.eyes_narrow()
    _assert_msg(bus, "enclosure.eyes.narrow", {})


def test_eyes_look(api, bus):
    api.eyes_look("u")
    _assert_msg(bus, "enclosure.eyes.look", {"side": "u"})


def test_eyes_color_defaults(api, bus):
    api.eyes_color()
    _assert_msg(bus, "enclosure.eyes.color", {"r": 255, "g": 255, "b": 255})


def test_eyes_color_custom(api, bus):
    api.eyes_color(r=10, g=20, b=30)
    _assert_msg(bus, "enclosure.eyes.color", {"r": 10, "g": 20, "b": 30})


def test_eyes_setpixel(api, bus):
    api.eyes_setpixel(5, r=1, g=2, b=3)
    _assert_msg(bus, "enclosure.eyes.setpixel",
                {"idx": 5, "r": 1, "g": 2, "b": 3})


@pytest.mark.parametrize("idx", [-1, 24, 100])
def test_eyes_setpixel_invalid_idx(api, bus, idx):
    with pytest.raises(ValueError):
        api.eyes_setpixel(idx)
    bus.emit.assert_not_called()


@pytest.mark.parametrize("idx", [0, 11, 12, 23])
def test_eyes_setpixel_boundary_idx(api, bus, idx):
    api.eyes_setpixel(idx)
    assert bus.emit.call_count == 1


def test_eyes_fill(api, bus):
    api.eyes_fill(75)
    _assert_msg(bus, "enclosure.eyes.fill", {"percentage": 75})


@pytest.mark.parametrize("pct", [-1, 101, 500])
def test_eyes_fill_invalid(api, bus, pct):
    with pytest.raises(ValueError):
        api.eyes_fill(pct)
    bus.emit.assert_not_called()


@pytest.mark.parametrize("pct", [0, 49, 50, 100])
def test_eyes_fill_boundary(api, bus, pct):
    api.eyes_fill(pct)
    assert bus.emit.call_count == 1


def test_eyes_brightness_default(api, bus):
    api.eyes_brightness()
    _assert_msg(bus, "enclosure.eyes.level", {"level": 30})


def test_eyes_brightness_custom(api, bus):
    api.eyes_brightness(15)
    _assert_msg(bus, "enclosure.eyes.level", {"level": 15})


def test_eyes_reset(api, bus):
    api.eyes_reset()
    _assert_msg(bus, "enclosure.eyes.reset", {})


def test_eyes_spin(api, bus):
    api.eyes_spin()
    _assert_msg(bus, "enclosure.eyes.spin", {})


def test_eyes_timed_spin(api, bus):
    api.eyes_timed_spin(2000)
    _assert_msg(bus, "enclosure.eyes.timedspin", {"length": 2000})


def test_eyes_volume(api, bus):
    api.eyes_volume(5)
    _assert_msg(bus, "enclosure.eyes.volume", {"volume": 5})


@pytest.mark.parametrize("vol", [-1, 12, 99])
def test_eyes_volume_invalid(api, bus, vol):
    with pytest.raises(ValueError):
        api.eyes_volume(vol)
    bus.emit.assert_not_called()


@pytest.mark.parametrize("vol", [0, 11])
def test_eyes_volume_boundary(api, bus, vol):
    api.eyes_volume(vol)
    assert bus.emit.call_count == 1


def test_mouth_reset(api, bus):
    api.mouth_reset()
    _assert_msg(bus, "enclosure.mouth.reset", {})


def test_mouth_talk(api, bus):
    api.mouth_talk()
    _assert_msg(bus, "enclosure.mouth.talk", {})


def test_mouth_think(api, bus):
    api.mouth_think()
    _assert_msg(bus, "enclosure.mouth.think", {})


def test_mouth_listen(api, bus):
    api.mouth_listen()
    _assert_msg(bus, "enclosure.mouth.listen", {})


def test_mouth_smile(api, bus):
    api.mouth_smile()
    _assert_msg(bus, "enclosure.mouth.smile", {})


def test_mouth_viseme(api, bus):
    pairs = [(0, 0.1), (4, 0.2)]
    api.mouth_viseme(123, pairs)
    _assert_msg(bus, "enclosure.mouth.viseme_list",
                {"start": 123, "visemes": pairs})


def test_mouth_text_default(api, bus):
    api.mouth_text()
    _assert_msg(bus, "enclosure.mouth.text", {"text": ""})


def test_mouth_text_custom(api, bus):
    api.mouth_text("hello")
    _assert_msg(bus, "enclosure.mouth.text", {"text": "hello"})


def test_mouth_display_defaults(api, bus):
    api.mouth_display()
    _assert_msg(bus, "enclosure.mouth.display",
                {"img_code": "", "xOffset": 0, "yOffset": 0, "clearPrev": True})


def test_mouth_display_custom(api, bus):
    api.mouth_display(img_code="abc", x=2, y=3, refresh=False)
    _assert_msg(bus, "enclosure.mouth.display",
                {"img_code": "abc", "xOffset": 2, "yOffset": 3,
                 "clearPrev": False})


def test_mouth_display_png_defaults(api, bus):
    api.mouth_display_png("/tmp/a.png")
    _assert_msg(bus, "enclosure.mouth.display_image",
                {"img_path": "/tmp/a.png", "xOffset": 0, "yOffset": 0,
                 "invert": False, "clearPrev": True})


def test_mouth_display_png_custom(api, bus):
    api.mouth_display_png("/tmp/b.png", invert=True, x=4, y=5, refresh=False)
    _assert_msg(bus, "enclosure.mouth.display_image",
                {"img_path": "/tmp/b.png", "xOffset": 4, "yOffset": 5,
                 "invert": True, "clearPrev": False})


def test_weather_display(api, bus):
    api.weather_display(3, 21)
    _assert_msg(bus, "enclosure.weather.display",
                {"img_code": 3, "temp": 21})


def test_activate_mouth_events(api, bus):
    api.activate_mouth_events()
    _assert_msg(bus, "enclosure.mouth.events.activate", {})


def test_deactivate_mouth_events(api, bus):
    api.deactivate_mouth_events()
    _assert_msg(bus, "enclosure.mouth.events.deactivate", {})


def test_get_eyes_color(api, bus):
    pixels = [(1, 2, 3)] * 24
    resp = MagicMock()
    resp.data = {"pixels": pixels}
    bus.wait_for_response.return_value = resp
    assert api.get_eyes_color() == pixels
    # request message is correct
    req = bus.wait_for_response.call_args[0][0]
    assert req.msg_type == "enclosure.eyes.rgb.get"
    assert bus.wait_for_response.call_args[0][1] == "enclosure.eyes.rgb"


def test_get_eyes_color_timeout(api, bus):
    bus.wait_for_response.return_value = None
    with pytest.raises(TimeoutError):
        api.get_eyes_color()


def test_get_eyes_pixel_color(api, bus):
    pixels = [(i, i, i) for i in range(24)]
    resp = MagicMock()
    resp.data = {"pixels": pixels}
    bus.wait_for_response.return_value = resp
    assert api.get_eyes_pixel_color(7) == (7, 7, 7)


@pytest.mark.parametrize("idx", [-1, 24])
def test_get_eyes_pixel_color_invalid(api, bus, idx):
    with pytest.raises(ValueError):
        api.get_eyes_pixel_color(idx)
    bus.wait_for_response.assert_not_called()
