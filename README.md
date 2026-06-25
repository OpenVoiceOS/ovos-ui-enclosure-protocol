# ovos-ui-enclosure-protocol

Canonical home of the legacy **Mark-1 hardware enclosure protocol** and the
`EnclosureAPI` producer helper for OpenVoiceOS.

`EnclosureAPI` is a thin, skill-facing helper that emits the `enclosure.*` bus
messages controlling the Mark-1 hardware enclosure: the LED eyes, the
mouth/faceplate display, and the system LEDs. Hardware enclosure PHAL plugins
listen for those messages and drive the actual hardware;
[`ovos-PHAL-plugin-mk1`](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-mk1)
is the reference listener implementation.

The enclosure protocol is **no longer a core abstraction**. All modern visual
output is done through `GUIInterface` (OVOS-GUI-1). This package exists so
mk1-specific skills and hardware integrations keep a stable, dependency-light
home for the producer side of the protocol. It does **not** reimplement GUI
templates.

## Install

```bash
pip install ovos-ui-enclosure-protocol
```

## Usage

```python
from ovos_ui_enclosure_protocol import EnclosureAPI

enclosure = EnclosureAPI(bus=bus, skill_id="my.skill")

enclosure.eyes_color(r=0, g=255, b=0)   # green eyes
enclosure.mouth_text("hello world")      # scroll text on faceplate
enclosure.eyes_blink("b")                # blink both eyes
enclosure.mouth_reset()                  # clear the faceplate
```

Every method forwards a single `enclosure.*` `Message` on the bus. Consumers
(hardware PHAL plugins) decide how — or whether — to render each command.

## Implementing a listener

Hardware enclosure plugins consume the same protocol via the
`EnclosureProtocolListener` mix-in:

```python
from ovos_ui_enclosure_protocol import EnclosureProtocolListener

class MyEnclosure(EnclosureProtocolListener):
    def __init__(self, bus):
        self.bus = bus
        self.register_enclosure_namespace()

    def on_eyes_color(self, message=None):
        ...  # drive the hardware
```

`ovos-PHAL-plugin-mk1` is the reference listener implementation.

## Migrating from ovos-bus-client

`EnclosureAPI` previously lived at `ovos_bus_client.apis.enclosure`. The public
method surface and the bus contract are identical here, so migration is an
import change only:

```python
# before
from ovos_bus_client.apis.enclosure import EnclosureAPI

# after
from ovos_ui_enclosure_protocol import EnclosureAPI
```

## Documentation

- [`docs/index.md`](docs/index.md) — overview, install, usage, migration.
- [`docs/enclosure-protocol.md`](docs/enclosure-protocol.md) — the full
  `enclosure.*` message contract with producers and listeners.

## License

Apache-2.0
