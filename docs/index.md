# ovos-ui-enclosure-protocol

The consumer/listener home of the legacy Mark-1 hardware enclosure protocol.

## What this package is

The `enclosure.*` bus messages drive Mark-1 hardware: the LED eyes, the
mouth/faceplate display, and the system LEDs. This is a two-sided protocol:

- **Producer** — `EnclosureAPI`, the skill-facing helper that emits
  `enclosure.*`. It lives in
  [`ovos-gui-api-client`](https://github.com/OpenVoiceOS/ovos-gui-api-client)
  alongside `GUIInterface`, so `self.gui` and `self.enclosure` come from the
  same client. This package does **not** reimplement it.
- **Listener** — `EnclosureProtocolListener` (this package), a consumer mix-in
  that wires the `enclosure.*` subscriptions to overridable no-op handlers, for
  hardware enclosure plugins.

The reference listener implementation is
[`ovos-PHAL-plugin-mk1`](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-mk1),
which subclasses `EnclosureProtocolListener`.

The enclosure protocol is **no longer a core abstraction**: `PHALPlugin` in
`ovos-plugin-manager` no longer bakes in the `enclosure.*` handlers. A hardware
plugin that wants enclosure-protocol support mixes in
`EnclosureProtocolListener` from this package instead. Modern visual output is
handled by `GUIInterface` (OVOS-GUI-1) and its template system; this package is
strictly the legacy hardware-enclosure protocol.

## Install

```bash
pip install ovos-ui-enclosure-protocol
```

The only runtime dependency is `ovos-bus-client` (for the bus message types).

## Implementing a listener

A hardware enclosure plugin inherits the mix-in, provides a connected
`self.bus`, wires the subscriptions, and overrides only the handlers its
hardware supports — every handler defaults to a no-op so unsupported events are
simply ignored:

```python
from ovos_ui_enclosure_protocol import EnclosureProtocolListener

class MyEnclosure(EnclosureProtocolListener):
    def __init__(self, bus):
        self.bus = bus
        self.register_enclosure_namespace()  # enclosure.* commands
        self.register_core_events()          # record/speak/wake/sleep lifecycle

    def on_eyes_color(self, message=None):
        r, g, b = message.data["r"], message.data["g"], message.data["b"]
        ...  # drive the hardware

    def on_record_begin(self, message=None):
        ...  # show a "listening" animation

    def shutdown(self):
        self.shutdown_enclosure_namespace()
        self.shutdown_core_events()
```

The listener wires two groups of events:

- **`register_enclosure_namespace()`** — the `enclosure.*` command topics (eyes,
  mouth/faceplate, system).
- **`register_core_events()`** — the core lifecycle an enclosure animates to:
  `recognizer_loop:record_begin`/`record_end`/`sleep`/`audio_output_start`/
  `audio_output_end`, `mycroft.awoken`, `speak`.

Mouth-animation commands (`talk`/`think`/`listen`/`smile`/`viseme`) are gated
by `mouth_events_active`, toggled via the
`enclosure.mouth.events.activate`/`deactivate` messages.

The mix-in needs only `self.bus`; it excludes the PHAL plugin lifecycle
(Thread/`run`/process management), which stays in `ovos-plugin-manager`'s
`PHALPlugin`.

## Emitting commands (producer)

Skills emit `enclosure.*` via `EnclosureAPI` from `ovos-gui-api-client`:

```python
from ovos_gui_api_client import EnclosureAPI

enclosure = EnclosureAPI(bus=bus, skill_id="my.skill")
enclosure.eyes_color(r=0, g=128, b=255)
enclosure.mouth_text("hello")
```

## See also

- [`enclosure-protocol.md`](enclosure-protocol.md) — the full `enclosure.*`
  message contract, listing producers and listeners.
