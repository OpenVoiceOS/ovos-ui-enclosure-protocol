"""ovos-ui-enclosure-protocol.

Consumer side of the legacy Mark-1 hardware enclosure protocol.

``EnclosureProtocolListener`` is a mix-in that a hardware enclosure plugin
inherits to wire the ``enclosure.*`` bus subscriptions to overridable no-op
handlers, so a plugin only implements the commands its hardware supports.
``ovos-PHAL-plugin-mk1`` is the reference listener implementation.

The producer side (``EnclosureAPI``, the skill-facing helper that emits the
``enclosure.*`` messages) lives in ``ovos-gui-api-client`` alongside
``GUIInterface`` — ``self.gui`` and ``self.enclosure`` come from the same
client. This package does not reimplement it.

The enclosure protocol is **no longer a core abstraction**: ``PHALPlugin`` in
``ovos-plugin-manager`` no longer wires ``enclosure.*`` handlers. A hardware
plugin that wants enclosure-protocol support mixes in
``EnclosureProtocolListener`` from this package instead. Modern visual output
is handled by ``GUIInterface`` (OVOS-GUI-1) and its template system.
"""
from ovos_ui_enclosure_protocol.listener import EnclosureProtocolListener
from ovos_ui_enclosure_protocol.version import __version__

__all__ = ["EnclosureProtocolListener", "__version__"]
