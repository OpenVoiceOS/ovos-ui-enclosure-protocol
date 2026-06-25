# ovos-ui-enclosure-protocol

The canonical home of the legacy Mark-1 hardware enclosure protocol and the
`EnclosureAPI` producer helper.

## What this package is

`EnclosureAPI` is the skill-facing helper that emits the `enclosure.*` bus
messages used to drive Mark-1 hardware: the LED eyes, the mouth/faceplate
display, and the system LEDs. Skills (the producers) call `EnclosureAPI`
methods; hardware enclosure PHAL plugins (the listeners) consume the resulting
messages and drive the hardware.

This package is the producer side and the protocol definition. The listener
side lives in hardware PHAL plugins, with
[`ovos-PHAL-plugin-mk1`](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-mk1)
as the reference implementation.

The enclosure protocol is **no longer a core abstraction**. Modern visual
output is handled by `GUIInterface` (OVOS-GUI-1) and its template system. This
package is strictly the legacy hardware-enclosure protocol; it does not
reimplement GUI templates.

## Install

```bash
pip install ovos-ui-enclosure-protocol
```

The only runtime dependency is `ovos-bus-client` (for `Message` and
`dig_for_message`).

## Using EnclosureAPI

Construct an `EnclosureAPI` with a connected `MessageBusClient` and your
`skill_id`, then call methods to emit enclosure commands:

```python
from ovos_ui_enclosure_protocol import EnclosureAPI

enclosure = EnclosureAPI(bus=bus, skill_id="my.skill")

# eyes
enclosure.eyes_on()
enclosure.eyes_color(r=0, g=128, b=255)
enclosure.eyes_blink("b")        # 'r', 'l' or 'b'
enclosure.eyes_fill(50)          # progress meter, 0-100
enclosure.eyes_reset()

# mouth / faceplate
enclosure.mouth_talk()
enclosure.mouth_text("hello")
enclosure.mouth_display_png("/path/to/image.png")
enclosure.mouth_reset()

# system
enclosure.system_blink(2)
enclosure.system_mute()
```

The bus and skill_id can also be set after construction:

```python
enclosure = EnclosureAPI()
enclosure.set_bus(bus)
enclosure.set_id("my.skill")
```

### Reading eye color back

`get_eyes_color()` and `get_eyes_pixel_color(idx)` issue a request/response
round-trip (`enclosure.eyes.rgb.get` → `enclosure.eyes.rgb`) and raise
`TimeoutError` if no listener responds.

### Input validation

A few methods guard their arguments and raise `ValueError`:

- `eyes_setpixel(idx, ...)` / `get_eyes_pixel_color(idx)` — `idx` must be 0-23.
- `eyes_fill(percentage)` — `percentage` must be 0-100.
- `eyes_volume(volume)` — `volume` must be 0-11.

## Migrating from ovos-bus-client

`EnclosureAPI` used to live at `ovos_bus_client.apis.enclosure`. It has been
removed from `ovos-bus-client` as a core abstraction and rehoused here, with
the public method surface and the bus contract kept identical. Migration is an
import change only:

```python
# before
from ovos_bus_client.apis.enclosure import EnclosureAPI

# after
from ovos_ui_enclosure_protocol import EnclosureAPI
```

## See also

- [`enclosure-protocol.md`](enclosure-protocol.md) — the full `enclosure.*`
  message contract, listing producers and listeners.
