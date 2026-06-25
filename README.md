# ovos-ui-enclosure-protocol

The consumer/listener home of the legacy **Mark-1 hardware enclosure protocol**
for OpenVoiceOS.

The `enclosure.*` bus messages control the Mark-1 hardware enclosure: the LED
eyes, the mouth/faceplate display, and the system LEDs. This package provides
`EnclosureProtocolListener`, a consumer mix-in that a hardware enclosure plugin
inherits to wire the `enclosure.*` subscriptions to overridable no-op handlers.
[`ovos-PHAL-plugin-mk1`](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-mk1)
is the reference listener implementation.

The producer side — `EnclosureAPI`, the skill-facing helper that *emits*
`enclosure.*` — lives in
[`ovos-gui-api-client`](https://github.com/OpenVoiceOS/ovos-gui-api-client)
alongside `GUIInterface`, so `self.gui` and `self.enclosure` come from the same
client.

The enclosure protocol is **no longer a core abstraction**: `PHALPlugin` in
`ovos-plugin-manager` no longer bakes in the `enclosure.*` handlers, and modern
visual output is done through `GUIInterface` (OVOS-GUI-1). This package exists
so hardware enclosure plugins keep a stable, dependency-light home for the
listener side of the protocol. It does **not** reimplement GUI templates.

## Install

```bash
pip install ovos-ui-enclosure-protocol
```

## Implementing a listener

```python
from ovos_ui_enclosure_protocol import EnclosureProtocolListener

class MyEnclosure(EnclosureProtocolListener):
    def __init__(self, bus):
        self.bus = bus
        self.register_enclosure_namespace()

    def on_eyes_color(self, message=None):
        ...  # drive the hardware

    def shutdown(self):
        self.shutdown_enclosure_namespace()
```

Every handler defaults to a no-op, so a plugin only overrides the commands its
hardware supports. `ovos-PHAL-plugin-mk1` is the reference listener
implementation.

## Documentation

- [`docs/index.md`](docs/index.md) — overview, install, listener guide.
- [`docs/enclosure-protocol.md`](docs/enclosure-protocol.md) — the full
  `enclosure.*` message contract with producers and listeners.

## License

Apache-2.0
