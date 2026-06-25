# The enclosure protocol

The enclosure protocol is the set of `enclosure.*` messagebus messages used to
control a Mark-1 style hardware enclosure: the LED eyes, the mouth/faceplate
display, and the system LEDs.

It is a two-sided protocol:

- **Producers** emit `enclosure.*` messages. The reference producer is
  `EnclosureAPI` (this package); any skill or component that wants to drive the
  enclosure uses it.
- **Listeners / consumers** subscribe to `enclosure.*` messages and drive the
  actual hardware. The reference listener is
  [`ovos-PHAL-plugin-mk1`](https://github.com/OpenVoiceOS/ovos-PHAL-plugin-mk1),
  which implements the full contract for the Mark-1 faceplate and eyes. Other
  enclosure hardware plugins implement the same contract for their own
  hardware; unsupported commands may simply be ignored.

This package owns the producer side and the protocol definition. The listeners
stay in the hardware PHAL plugins. The protocol is **not** a core abstraction —
only hardware enclosure plugins should listen; generic/core enclosure-event
listeners do not belong anywhere else.

All messages are emitted via `Message.forward(...)`, so they inherit context
(including `skill_id` and a `destination` of `["enclosure"]`) from the inbound
message when one is available.

## Message contract

### Lifecycle / active skill

| Message type | Data | Producer method | Meaning |
|---|---|---|---|
| `enclosure.active_skill` | `{skill_id}` | `register(skill_id="")` | Mark a skill as the active enclosure skill. Deprecated/unused, kept for compatibility. |
| `enclosure.reset` | — | `reset()` | Restore the enclosure to its started state (eyes open, mouth at default). |

### System

| Message type | Data | Producer method | Meaning |
|---|---|---|---|
| `enclosure.system.reset` | — | `system_reset()` | Reset enclosure hardware CPUs etc. |
| `enclosure.system.mute` | — | `system_mute()` | Mute (turn off) the system speaker. |
| `enclosure.system.unmute` | — | `system_unmute()` | Unmute (turn on) the system speaker. |
| `enclosure.system.blink` | `{times}` | `system_blink(times)` | Blink the eyes `times` times. |

### Eyes

| Message type | Data | Producer method | Meaning |
|---|---|---|---|
| `enclosure.eyes.on` | — | `eyes_on()` | Illuminate / show the eyes. |
| `enclosure.eyes.off` | — | `eyes_off()` | Turn off / hide the eyes. |
| `enclosure.eyes.blink` | `{side}` | `eyes_blink(side)` | Blink eyes. `side` is `'r'`, `'l'` or `'b'`. |
| `enclosure.eyes.narrow` | — | `eyes_narrow()` | Narrow the eyes (squint). |
| `enclosure.eyes.look` | `{side}` | `eyes_look(side)` | Look toward a side: `'r'`, `'l'`, `'u'`, `'d'`, `'c'`. |
| `enclosure.eyes.color` | `{r, g, b}` | `eyes_color(r=255, g=255, b=255)` | Set the eye color (all pixels). |
| `enclosure.eyes.setpixel` | `{idx, r, g, b}` | `eyes_setpixel(idx, r=255, g=255, b=255)` | Set a single neopixel. `idx` 0-11 right eye, 12-23 left. Raises `ValueError` if `idx` outside 0-23. |
| `enclosure.eyes.fill` | `{percentage}` | `eyes_fill(percentage)` | Use the eyes as a progress meter. 0-49 fills right eye, 50-100 also covers left. Raises `ValueError` if outside 0-100. |
| `enclosure.eyes.level` | `{level}` | `eyes_brightness(level=30)` | Set eye brightness, 1-30. |
| `enclosure.eyes.reset` | — | `eyes_reset()` | Restore eyes to the default (ready) state. |
| `enclosure.eyes.spin` | — | `eyes_spin()` | Make the eyes roll. |
| `enclosure.eyes.timedspin` | `{length}` | `eyes_timed_spin(length)` | Roll the eyes for `length` ms (`None` = forever). |
| `enclosure.eyes.volume` | `{volume}` | `eyes_volume(volume)` | Indicate volume on the eyes, 0-11. Raises `ValueError` if outside 0-11. |
| `enclosure.eyes.rgb.get` | — | `get_eyes_color()` / `get_eyes_pixel_color(idx)` | Request the current eye pixel colors. Expects a response on `enclosure.eyes.rgb`. |
| `enclosure.eyes.rgb` | `{pixels}` | (listener response) | Response carrying the list of `(r, g, b)` pixel tuples. `get_eyes_color()` raises `TimeoutError` if no response arrives. |

### Mouth / faceplate

| Message type | Data | Producer method | Meaning |
|---|---|---|---|
| `enclosure.mouth.reset` | — | `mouth_reset()` | Restore the mouth display to blank. |
| `enclosure.mouth.talk` | — | `mouth_talk()` | Generic talking animation (non-synched speech). |
| `enclosure.mouth.think` | — | `mouth_think()` | Thinking image / animation. |
| `enclosure.mouth.listen` | — | `mouth_listen()` | Listening image / animation. |
| `enclosure.mouth.smile` | — | `mouth_smile()` | Smile image / animation. |
| `enclosure.mouth.text` | `{text}` | `mouth_text(text="")` | Display text, scrolling as needed. |
| `enclosure.mouth.display` | `{img_code, xOffset, yOffset, clearPrev}` | `mouth_display(img_code="", x=0, y=0, refresh=True)` | Display an encoded black/white image (up to 16x8). |
| `enclosure.mouth.display_image` | `{img_path, xOffset, yOffset, invert, clearPrev}` | `mouth_display_png(image_absolute_path, invert=False, x=0, y=0, refresh=True)` | Display an image file on the faceplate. |
| `enclosure.mouth.viseme_list` | `{start, visemes}` | `mouth_viseme(start, viseme_pairs)` | Send mouth visemes as `(code, end_time)` pairs for speech sync. |
| `enclosure.mouth.events.activate` | — | `activate_mouth_events()` | Enable mouth movement with speech. |
| `enclosure.mouth.events.deactivate` | — | `deactivate_mouth_events()` | Disable mouth movement with speech. |

### Weather

| Message type | Data | Producer method | Meaning |
|---|---|---|---|
| `enclosure.weather.display` | `{img_code, temp}` | `weather_display(img_code, temp)` | Show a weather icon and temperature. `img_code` 0-7 (sunny, partly cloudy, cloudy, light rain, raining, stormy, snowing, wind/mist). |

## Viseme codes

`mouth_viseme(start, viseme_pairs)` sends `(code, cumulative_end_time)` pairs.
The codes are:

| Code | Shape for sounds like |
|---|---|
| 0 | `y`, `aa` |
| 1 | `aw` |
| 2 | `uh`, `r` |
| 3 | `th`, `sh` |
| 4 | neutral / no sound |
| 5 | `f`, `v` |
| 6 | `oy`, `ao` |
