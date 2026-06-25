"""ovos-ui-enclosure-protocol.

Canonical home of the legacy Mark-1 hardware enclosure protocol and the
``EnclosureAPI`` producer helper. ``EnclosureAPI`` emits the ``enclosure.*``
bus messages that hardware enclosure PHAL plugins (``ovos-PHAL-plugin-mk1``
being the reference listener) consume to drive eyes, mouth/faceplate and
system LEDs.

The consumer side is the ``EnclosureProtocolListener`` mix-in, which a hardware
enclosure plugin inherits to wire the ``enclosure.*`` subscriptions to
overridable no-op handlers (``ovos-PHAL-plugin-mk1`` is the reference
implementation).

This is the legacy hardware-enclosure protocol only. Modern visual output is
handled by ``GUIInterface`` (OVOS-GUI-1); this package does not reimplement
GUI templates.
"""
from ovos_ui_enclosure_protocol.enclosure import EnclosureAPI
from ovos_ui_enclosure_protocol.listener import EnclosureProtocolListener
from ovos_ui_enclosure_protocol.version import __version__

__all__ = ["EnclosureAPI", "EnclosureProtocolListener", "__version__"]
