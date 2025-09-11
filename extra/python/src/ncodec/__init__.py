"""
AutomotiveBus Package

This package provides automotive bus communication codecs and interfaces
for encoding and decoding various automotive protocols like CAN and PDU.
"""

from .codec_interface import (
    ICodec,
    CodecFactory,
    MessageType
)

from .pdu import PduCodec, PduMessage
from .can import CanCodec, CanMessage

__all__ = [
    # Interfaces
    'ICodec',
    'CodecFactory',
    'MessageType',
    
    # Concrete implementations
    'PduCodec',
    'PduMessage',
    'CanCodec',
    'CanMessage',
]

__version__ = "1.0.0"

# Compatibility shims: re-export commonly-used flatbuffer enums/classes from the
# generated AutomotiveBus package so existing tests and examples that expect
# `AutomotiveBus`-style imports can access them through `ncodec`.
from AutomotiveBus.Stream.Pdu.TransportMetadata import TransportMetadata
from AutomotiveBus.Stream.Frame.CanFrameType import CanFrameType

# Export compatibility names
__all__.extend([
    'TransportMetadata',
    'CanFrameType',
])