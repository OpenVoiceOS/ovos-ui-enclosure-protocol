"""Consumer side of the enclosure protocol.

``EnclosureProtocolListener`` is a mix-in that wires the bus messages an
enclosure reacts to — both the ``enclosure.*`` commands emitted by
:class:`EnclosureAPI` and the core lifecycle events (record/speak/wake/sleep)
that an enclosure animates to — to overridable no-op handler methods. A
hardware enclosure plugin inherits this mix-in and only overrides the handlers
it cares about.

The mix-in needs only ``self.bus``; it does not include the PHAL plugin
lifecycle (Thread/run/process management), which stays in
``ovos-plugin-manager``'s ``PHALPlugin``.

``ovos-PHAL-plugin-mk1`` is the reference implementation that subclasses this
listener.
"""


class EnclosureProtocolListener:
    """Mix-in that subscribes a hardware plugin to the enclosure protocol.

    Subclasses provide a ``self.bus`` (a connected ``MessageBusClient``) and
    call :meth:`register_enclosure_namespace` (the ``enclosure.*`` commands) and
    :meth:`register_core_events` (the record/speak/wake/sleep lifecycle the
    enclosure animates to), then override the ``on_*`` handlers they support.
    Every handler defaults to a no-op so unsupported events are simply ignored.
    """

    _mouth_events = False

    def register_core_events(self):
        """Wire the core lifecycle bus events an enclosure animates to."""
        self.bus.on('recognizer_loop:record_begin', self.on_record_begin)
        self.bus.on('recognizer_loop:record_end', self.on_record_end)
        self.bus.on("recognizer_loop:sleep", self.on_sleep)
        self.bus.on('recognizer_loop:audio_output_start', self.on_audio_output_start)
        self.bus.on('recognizer_loop:audio_output_end', self.on_audio_output_end)
        self.bus.on("mycroft.awoken", self.on_awake)
        self.bus.on("speak", self.on_speak)

    def shutdown_core_events(self):
        """Remove the core lifecycle subscriptions wired by register_core_events."""
        self.bus.remove('recognizer_loop:record_begin', self.on_record_begin)
        self.bus.remove('recognizer_loop:record_end', self.on_record_end)
        self.bus.remove("recognizer_loop:sleep", self.on_sleep)
        self.bus.remove('recognizer_loop:audio_output_start', self.on_audio_output_start)
        self.bus.remove('recognizer_loop:audio_output_end', self.on_audio_output_end)
        self.bus.remove("mycroft.awoken", self.on_awake)
        self.bus.remove("speak", self.on_speak)

    # Core lifecycle handlers (no-ops by default)
    def on_record_begin(self, message=None):
        """Listening started (``recognizer_loop:record_begin``)."""
        pass

    def on_record_end(self, message=None):
        """Listening ended (``recognizer_loop:record_end``)."""
        pass

    def on_audio_output_start(self, message=None):
        """Speaking started (``recognizer_loop:audio_output_start``)."""
        pass

    def on_audio_output_end(self, message=None):
        """Speaking ended (``recognizer_loop:audio_output_end``)."""
        pass

    def on_awake(self, message=None):
        """Wakeup animation (``mycroft.awoken``)."""
        pass

    def on_sleep(self, message=None):
        """Naptime animation (``recognizer_loop:sleep``)."""
        pass

    def on_speak(self, message=None):
        """A ``speak`` message; for enclosures that disregard visemes."""
        pass

    def register_enclosure_namespace(self):
        """Wire all ``enclosure.*`` messages to this listener's handlers."""
        self.bus.on("enclosure.notify.no_internet", self.on_no_internet)
        self.bus.on("enclosure.reset", self.on_reset)

        # enclosure commands for the system
        self.bus.on("enclosure.system.reset", self.on_system_reset)
        self.bus.on("enclosure.system.mute", self.on_system_mute)
        self.bus.on("enclosure.system.unmute", self.on_system_unmute)
        self.bus.on("enclosure.system.blink", self.on_system_blink)

        # enclosure commands for eyes
        self.bus.on("enclosure.eyes.on", self.on_eyes_on)
        self.bus.on("enclosure.eyes.off", self.on_eyes_off)
        self.bus.on("enclosure.eyes.blink", self.on_eyes_blink)
        self.bus.on("enclosure.eyes.narrow", self.on_eyes_narrow)
        self.bus.on("enclosure.eyes.look", self.on_eyes_look)
        self.bus.on("enclosure.eyes.color", self.on_eyes_color)
        self.bus.on("enclosure.eyes.level", self.on_eyes_brightness)
        self.bus.on("enclosure.eyes.volume", self.on_eyes_volume)
        self.bus.on("enclosure.eyes.spin", self.on_eyes_spin)
        self.bus.on("enclosure.eyes.timedspin", self.on_eyes_timed_spin)
        self.bus.on("enclosure.eyes.reset", self.on_eyes_reset)
        self.bus.on("enclosure.eyes.setpixel", self.on_eyes_set_pixel)
        self.bus.on("enclosure.eyes.fill", self.on_eyes_fill)

        # enclosure commands for mouth
        self.bus.on("enclosure.mouth.events.activate", self._activate_mouth_events)
        self.bus.on("enclosure.mouth.events.deactivate", self._deactivate_mouth_events)
        self.bus.on("enclosure.mouth.talk", self._on_mouth_talk)
        self.bus.on("enclosure.mouth.think", self._on_mouth_think)
        self.bus.on("enclosure.mouth.listen", self._on_mouth_listen)
        self.bus.on("enclosure.mouth.smile", self._on_mouth_smile)
        self.bus.on("enclosure.mouth.viseme", self._on_mouth_viseme)
        self.bus.on("enclosure.mouth.viseme_list", self._on_mouth_viseme_list)

        # mouth / matrix display
        self.bus.on("enclosure.mouth.reset", self.on_display_reset)
        self.bus.on("enclosure.mouth.text", self.on_text)
        self.bus.on("enclosure.mouth.display", self.on_display)
        self.bus.on("enclosure.weather.display", self.on_weather_display)

    def shutdown_enclosure_namespace(self):
        """Remove all ``enclosure.*`` subscriptions wired by this listener."""
        self.bus.remove("enclosure.notify.no_internet", self.on_no_internet)
        self.bus.remove("enclosure.reset", self.on_reset)

        self.bus.remove("enclosure.system.reset", self.on_system_reset)
        self.bus.remove("enclosure.system.mute", self.on_system_mute)
        self.bus.remove("enclosure.system.unmute", self.on_system_unmute)
        self.bus.remove("enclosure.system.blink", self.on_system_blink)

        self.bus.remove("enclosure.eyes.on", self.on_eyes_on)
        self.bus.remove("enclosure.eyes.off", self.on_eyes_off)
        self.bus.remove("enclosure.eyes.blink", self.on_eyes_blink)
        self.bus.remove("enclosure.eyes.narrow", self.on_eyes_narrow)
        self.bus.remove("enclosure.eyes.look", self.on_eyes_look)
        self.bus.remove("enclosure.eyes.color", self.on_eyes_color)
        self.bus.remove("enclosure.eyes.level", self.on_eyes_brightness)
        self.bus.remove("enclosure.eyes.volume", self.on_eyes_volume)
        self.bus.remove("enclosure.eyes.spin", self.on_eyes_spin)
        self.bus.remove("enclosure.eyes.timedspin", self.on_eyes_timed_spin)
        self.bus.remove("enclosure.eyes.reset", self.on_eyes_reset)
        self.bus.remove("enclosure.eyes.setpixel", self.on_eyes_set_pixel)
        self.bus.remove("enclosure.eyes.fill", self.on_eyes_fill)

        self.bus.remove("enclosure.mouth.events.activate", self._activate_mouth_events)
        self.bus.remove("enclosure.mouth.events.deactivate", self._deactivate_mouth_events)
        self.bus.remove("enclosure.mouth.talk", self._on_mouth_talk)
        self.bus.remove("enclosure.mouth.think", self._on_mouth_think)
        self.bus.remove("enclosure.mouth.listen", self._on_mouth_listen)
        self.bus.remove("enclosure.mouth.smile", self._on_mouth_smile)
        self.bus.remove("enclosure.mouth.viseme", self._on_mouth_viseme)
        self.bus.remove("enclosure.mouth.viseme_list", self._on_mouth_viseme_list)

        self.bus.remove("enclosure.mouth.reset", self.on_display_reset)
        self.bus.remove("enclosure.mouth.text", self.on_text)
        self.bus.remove("enclosure.mouth.display", self.on_display)
        self.bus.remove("enclosure.weather.display", self.on_weather_display)

    # Lifecycle
    def on_reset(self, message=None):
        """The enclosure should restore itself to a started state.
        Typically this would be represented by the eyes being 'open'
        and the mouth reset to its default (smile or blank).
        """
        pass

    def on_no_internet(self, message=None):
        """Handle the no-internet notification."""
        pass

    # System events
    def on_system_reset(self, message=None):
        """The enclosure hardware should reset any CPUs, etc."""
        pass

    def on_system_mute(self, message=None):
        """Mute (turn off) the system speaker."""
        pass

    def on_system_unmute(self, message=None):
        """Unmute (turn on) the system speaker."""
        pass

    def on_system_blink(self, message=None):
        """The 'eyes' should blink the given number of times."""
        pass

    # Eyes events
    def on_eyes_on(self, message=None):
        """Illuminate or show the eyes."""
        pass

    def on_eyes_off(self, message=None):
        """Turn off or hide the eyes."""
        pass

    def on_eyes_fill(self, message=None):
        """Use the eyes as a type of progress meter."""
        pass

    def on_eyes_blink(self, message=None):
        """Make the eyes blink."""
        pass

    def on_eyes_narrow(self, message=None):
        """Make the eyes look narrow, like a squint."""
        pass

    def on_eyes_look(self, message=None):
        """Make the eyes look to the given side."""
        pass

    def on_eyes_color(self, message=None):
        """Change the eye color to the given RGB color."""
        pass

    def on_eyes_brightness(self, message=None):
        """Set the brightness of the eyes in the display."""
        pass

    def on_eyes_reset(self, message=None):
        """Restore the eyes to their default (ready) state."""
        pass

    def on_eyes_timed_spin(self, message=None):
        """Make the eyes 'roll' for the given time."""
        pass

    def on_eyes_volume(self, message=None):
        """Indicate the volume using the eyes."""
        pass

    def on_eyes_spin(self, message=None):
        """Make the eyes 'roll'."""
        pass

    def on_eyes_set_pixel(self, message=None):
        """Set individual pixels of the neopixel eyes."""
        pass

    # Mouth events (gated by mouth_events_active)
    def _on_mouth_talk(self, message=None):
        """Show a generic 'talking' animation for non-synched speech."""
        if self.mouth_events_active:
            self.on_talk(message)

    def _on_mouth_think(self, message=None):
        """Show a 'thinking' image or animation."""
        if self.mouth_events_active:
            self.on_think(message)

    def _on_mouth_listen(self, message=None):
        """Show a 'listening' image or animation."""
        if self.mouth_events_active:
            self.on_listen(message)

    def _on_mouth_smile(self, message=None):
        """Show a 'smile' image or animation."""
        if self.mouth_events_active:
            self.on_smile(message)

    def _on_mouth_viseme(self, message=None):
        """Display a viseme mouth shape for synched speech."""
        if self.mouth_events_active:
            self.on_viseme(message)

    def _on_mouth_viseme_list(self, message=None):
        """Handle mouth visemes sent as a list in a single message."""
        if self.mouth_events_active:
            self.on_viseme_list(message)

    # Display (faceplate) events
    def on_display_reset(self, message=None):
        """Restore the mouth display to normal (blank)."""
        pass

    def on_talk(self, message=None):
        """Show a generic 'talking' animation for non-synched speech."""
        pass

    def on_think(self, message=None):
        """Show a 'thinking' image or animation."""
        pass

    def on_listen(self, message=None):
        """Show a 'listening' image or animation."""
        pass

    def on_smile(self, message=None):
        """Show a 'smile' image or animation."""
        pass

    def on_viseme(self, message=None):
        """Display a viseme mouth shape for synched speech."""
        pass

    def on_viseme_list(self, message=None):
        """Handle mouth visemes sent as a list in a single message."""
        pass

    def on_text(self, message=None):
        """Display text (scrolling as needed)."""
        pass

    def on_display(self, message=None):
        """Display images on the faceplate."""
        pass

    def on_weather_display(self, message=None):
        """Show the temperature and a weather icon."""
        pass

    # Mouth-event gating
    @property
    def mouth_events_active(self):
        return self._mouth_events

    def _activate_mouth_events(self, message=None):
        """Enable movement of the mouth with speech."""
        self._mouth_events = True

    def _deactivate_mouth_events(self, message=None):
        """Disable movement of the mouth with speech."""
        self._mouth_events = False
