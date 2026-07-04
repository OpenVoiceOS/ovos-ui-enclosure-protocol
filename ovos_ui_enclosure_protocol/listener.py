"""Consumer side of the enclosure protocol.

``EnclosureProtocolListener`` subscribes to the bus messages an enclosure
reacts to — both the ``enclosure.*`` commands emitted by :class:`EnclosureAPI`
and the core lifecycle events (record/speak/wake/sleep) an enclosure animates
to — and routes each to a **callback** the consumer supplies.

A hardware enclosure plugin **instantiates** it (composition; it is not a
mix-in), passing the bus and a callback per event it cares about. Each callback
is an explicit keyword argument for discoverability::

    self.enclosure = EnclosureProtocolListener(
        bus=self.bus,
        on_eyes_color=self._drive_eyes_color,
        on_record_begin=self._show_listening,
    )

Any event whose callback is omitted is ignored. The mouth-animation callbacks
(``on_talk``/``on_think``/``on_listen``/``on_smile``/``on_viseme``/
``on_viseme_list``) only fire while mouth events are active (see
:meth:`activate_mouth_events`).

``ovos-PHAL-plugin-mk1`` is the reference consumer.
"""

from ovos_spec_tools import SpecMessage


class EnclosureProtocolListener:
    """Route enclosure-protocol bus messages to per-event callbacks.

    Every callback takes a single ``message`` argument and defaults to ``None``
    (the event is ignored). Callbacks may also be (re)assigned after
    construction with :meth:`set_callback`.

    Args:
        bus: a connected ``MessageBusClient``. When given, the subscriptions are
            wired immediately; otherwise call :meth:`set_bus` later.

        on_record_begin: voice-command capture started (``ovos.listener.record.started``).
        on_record_end: voice-command capture ended (``ovos.listener.record.ended``).
        on_sleep: entered sleep mode (``ovos.listener.sleep``).
        on_audio_output_start: TTS playback started (``ovos.audio.output.started``).
        on_audio_output_end: TTS playback ended (``ovos.audio.output.ended``).
        on_awoken: left sleep mode (``ovos.listener.awoken``).
        on_speak: a ``ovos.utterance.speak`` message; for enclosures that disregard visemes.

        on_no_internet: no-internet notification (``enclosure.notify.no_internet``).
        on_reset: restore the enclosure to its started state (``enclosure.reset``).
        on_system_reset: reset enclosure hardware (``enclosure.system.reset``).
        on_system_mute: mute the system speaker (``enclosure.system.mute``).
        on_system_unmute: unmute the system speaker (``enclosure.system.unmute``).
        on_system_blink: blink the eyes N times (``enclosure.system.blink``).

        on_eyes_on: illuminate the eyes (``enclosure.eyes.on``).
        on_eyes_off: turn off the eyes (``enclosure.eyes.off``).
        on_eyes_fill: use the eyes as a progress meter (``enclosure.eyes.fill``).
        on_eyes_blink: blink the eyes (``enclosure.eyes.blink``).
        on_eyes_narrow: narrow the eyes (``enclosure.eyes.narrow``).
        on_eyes_look: look to a side (``enclosure.eyes.look``).
        on_eyes_color: set the eye color (``enclosure.eyes.color``).
        on_eyes_brightness: set eye brightness (``enclosure.eyes.level``).
        on_eyes_reset: restore eyes to default (``enclosure.eyes.reset``).
        on_eyes_timed_spin: roll the eyes for a time (``enclosure.eyes.timedspin``).
        on_eyes_volume: indicate volume on the eyes (``enclosure.eyes.volume``).
        on_eyes_spin: roll the eyes (``enclosure.eyes.spin``).
        on_eyes_set_pixel: set a single neopixel (``enclosure.eyes.setpixel``).

        on_talk: talking animation (``enclosure.mouth.talk``; mouth-gated).
        on_think: thinking animation (``enclosure.mouth.think``; mouth-gated).
        on_listen: listening animation (``enclosure.mouth.listen``; mouth-gated).
        on_smile: smile animation (``enclosure.mouth.smile``; mouth-gated).
        on_viseme: a viseme mouth shape (``enclosure.mouth.viseme``; mouth-gated).
        on_viseme_list: a viseme list (``enclosure.mouth.viseme_list``; mouth-gated).

        on_display_reset: blank the mouth display (``enclosure.mouth.reset``).
        on_text: display scrolling text (``enclosure.mouth.text``).
        on_display: display a faceplate image (``enclosure.mouth.display``).
        on_weather_display: show temperature + weather icon (``enclosure.weather.display``).
    """

    # callback name -> (bus topic, mouth-event-gated)
    CORE_EVENTS = {
        "on_record_begin": (SpecMessage.LISTENER_RECORD_STARTED, False),
        "on_record_end": (SpecMessage.LISTENER_RECORD_ENDED, False),
        "on_sleep": (SpecMessage.LISTENER_SLEEP, False),
        "on_audio_output_start": (SpecMessage.AUDIO_OUTPUT_STARTED, False),
        "on_audio_output_end": (SpecMessage.AUDIO_OUTPUT_ENDED, False),
        "on_awoken": (SpecMessage.LISTENER_AWOKEN, False),
        "on_speak": (SpecMessage.SPEAK, False),
    }
    ENCLOSURE_EVENTS = {
        "on_no_internet": ("enclosure.notify.no_internet", False),
        "on_reset": ("enclosure.reset", False),
        "on_system_reset": ("enclosure.system.reset", False),
        "on_system_mute": ("enclosure.system.mute", False),
        "on_system_unmute": ("enclosure.system.unmute", False),
        "on_system_blink": ("enclosure.system.blink", False),
        "on_eyes_on": ("enclosure.eyes.on", False),
        "on_eyes_off": ("enclosure.eyes.off", False),
        "on_eyes_blink": ("enclosure.eyes.blink", False),
        "on_eyes_narrow": ("enclosure.eyes.narrow", False),
        "on_eyes_look": ("enclosure.eyes.look", False),
        "on_eyes_color": ("enclosure.eyes.color", False),
        "on_eyes_brightness": ("enclosure.eyes.level", False),
        "on_eyes_volume": ("enclosure.eyes.volume", False),
        "on_eyes_spin": ("enclosure.eyes.spin", False),
        "on_eyes_timed_spin": ("enclosure.eyes.timedspin", False),
        "on_eyes_reset": ("enclosure.eyes.reset", False),
        "on_eyes_set_pixel": ("enclosure.eyes.setpixel", False),
        "on_eyes_fill": ("enclosure.eyes.fill", False),
        "on_talk": ("enclosure.mouth.talk", True),
        "on_think": ("enclosure.mouth.think", True),
        "on_listen": ("enclosure.mouth.listen", True),
        "on_smile": ("enclosure.mouth.smile", True),
        "on_viseme": ("enclosure.mouth.viseme", True),
        "on_viseme_list": ("enclosure.mouth.viseme_list", True),
        "on_display_reset": ("enclosure.mouth.reset", False),
        "on_text": ("enclosure.mouth.text", False),
        "on_display": ("enclosure.mouth.display", False),
        "on_weather_display": ("enclosure.weather.display", False),
    }

    def __init__(self, bus=None,
                 on_record_begin=None,
                 on_record_end=None,
                 on_sleep=None,
                 on_audio_output_start=None,
                 on_audio_output_end=None,
                 on_awoken=None,
                 on_speak=None,
                 on_no_internet=None,
                 on_reset=None,
                 on_system_reset=None,
                 on_system_mute=None,
                 on_system_unmute=None,
                 on_system_blink=None,
                 on_eyes_on=None,
                 on_eyes_off=None,
                 on_eyes_fill=None,
                 on_eyes_blink=None,
                 on_eyes_narrow=None,
                 on_eyes_look=None,
                 on_eyes_color=None,
                 on_eyes_brightness=None,
                 on_eyes_reset=None,
                 on_eyes_timed_spin=None,
                 on_eyes_volume=None,
                 on_eyes_spin=None,
                 on_eyes_set_pixel=None,
                 on_talk=None,
                 on_think=None,
                 on_listen=None,
                 on_smile=None,
                 on_viseme=None,
                 on_viseme_list=None,
                 on_display_reset=None,
                 on_text=None,
                 on_display=None,
                 on_weather_display=None):
        self.bus = bus
        self._mouth_events = False
        self._dispatchers = {}  # callback name -> stable bound dispatcher
        self._callbacks = {
            "on_record_begin": on_record_begin,
            "on_record_end": on_record_end,
            "on_sleep": on_sleep,
            "on_audio_output_start": on_audio_output_start,
            "on_audio_output_end": on_audio_output_end,
            "on_awoken": on_awoken,
            "on_speak": on_speak,
            "on_no_internet": on_no_internet,
            "on_reset": on_reset,
            "on_system_reset": on_system_reset,
            "on_system_mute": on_system_mute,
            "on_system_unmute": on_system_unmute,
            "on_system_blink": on_system_blink,
            "on_eyes_on": on_eyes_on,
            "on_eyes_off": on_eyes_off,
            "on_eyes_fill": on_eyes_fill,
            "on_eyes_blink": on_eyes_blink,
            "on_eyes_narrow": on_eyes_narrow,
            "on_eyes_look": on_eyes_look,
            "on_eyes_color": on_eyes_color,
            "on_eyes_brightness": on_eyes_brightness,
            "on_eyes_reset": on_eyes_reset,
            "on_eyes_timed_spin": on_eyes_timed_spin,
            "on_eyes_volume": on_eyes_volume,
            "on_eyes_spin": on_eyes_spin,
            "on_eyes_set_pixel": on_eyes_set_pixel,
            "on_talk": on_talk,
            "on_think": on_think,
            "on_listen": on_listen,
            "on_smile": on_smile,
            "on_viseme": on_viseme,
            "on_viseme_list": on_viseme_list,
            "on_display_reset": on_display_reset,
            "on_text": on_text,
            "on_display": on_display,
            "on_weather_display": on_weather_display,
        }
        if self.bus is not None:
            self.register()

    def set_bus(self, bus):
        """Attach a bus and wire all subscriptions."""
        self.bus = bus
        self.register()

    def set_callback(self, name, callback):
        """Register (or replace) the callback for a single event name.

        ``name`` is one of the ``on_*`` keys (see :attr:`ENCLOSURE_EVENTS` /
        :attr:`CORE_EVENTS`).
        """
        if name not in self._callbacks:
            raise KeyError(f"unknown enclosure callback: {name}")
        self._callbacks[name] = callback

    # ---- mouth-event gating ----------------------------------------------
    @property
    def mouth_events_active(self):
        return self._mouth_events

    def activate_mouth_events(self, message=None):
        """Enable mouth-animation callbacks (talk/think/listen/...)."""
        self._mouth_events = True

    def deactivate_mouth_events(self, message=None):
        """Disable mouth-animation callbacks."""
        self._mouth_events = False

    # ---- dispatch --------------------------------------------------------
    def _dispatcher(self, name, gated):
        """A stable per-event dispatcher that invokes the registered callback."""
        if name not in self._dispatchers:
            def dispatch(message=None):
                if gated and not self._mouth_events:
                    return
                cb = self._callbacks.get(name)
                if cb is not None:
                    cb(message)
            self._dispatchers[name] = dispatch
        return self._dispatchers[name]

    # ---- registration ----------------------------------------------------
    def register(self):
        """Wire the enclosure.* commands and the core lifecycle events."""
        self.register_enclosure_namespace()
        self.register_core_events()

    def shutdown(self):
        """Remove every subscription wired by :meth:`register`."""
        self.shutdown_enclosure_namespace()
        self.shutdown_core_events()

    def register_core_events(self):
        """Wire the core lifecycle bus events an enclosure animates to."""
        for name, (topic, gated) in self.CORE_EVENTS.items():
            self.bus.on(topic, self._dispatcher(name, gated))

    def shutdown_core_events(self):
        """Remove the core lifecycle subscriptions."""
        for name, (topic, gated) in self.CORE_EVENTS.items():
            self.bus.remove(topic, self._dispatcher(name, gated))

    def register_enclosure_namespace(self):
        """Wire the ``enclosure.*`` command messages."""
        self.bus.on("enclosure.mouth.events.activate", self.activate_mouth_events)
        self.bus.on("enclosure.mouth.events.deactivate", self.deactivate_mouth_events)
        for name, (topic, gated) in self.ENCLOSURE_EVENTS.items():
            self.bus.on(topic, self._dispatcher(name, gated))

    def shutdown_enclosure_namespace(self):
        """Remove the ``enclosure.*`` subscriptions."""
        self.bus.remove("enclosure.mouth.events.activate", self.activate_mouth_events)
        self.bus.remove("enclosure.mouth.events.deactivate", self.deactivate_mouth_events)
        for name, (topic, gated) in self.ENCLOSURE_EVENTS.items():
            self.bus.remove(topic, self._dispatcher(name, gated))
