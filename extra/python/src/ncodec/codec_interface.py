#!/usr/bin/env python3
"""
Codec Interface Module

This module provides a common interface for automotive bus codecs
including PDU and CAN frame encoding/decoding operations.
"""

from abc import ABC, abstractmethod
from ncodec.mimetype import decode_mime_type
from typing import List, TypeVar, Generic, Optional, Dict

# Generic type for message types (CanMessage, PduMessage, etc.)
MessageType = TypeVar('MessageType')

class ICodec(ABC, Generic[MessageType]):

    def __init__(self, MimeMap: Dict[str, str], Stream: bytearray, ModelName: str, SimulationTime: float):
        self.MimeMap = MimeMap
        self.Stream = Stream
        self.ModelName = ModelName
        self.SimulationTime = SimulationTime

    @abstractmethod
    def Write(self, msgs: List[MessageType]) -> None:
        pass

    @abstractmethod
    def Read(self) -> List[MessageType]:
        pass

    @abstractmethod
    def Flush(self) -> None:
        pass

    @abstractmethod
    def Truncate(self) -> None:
        pass

    @abstractmethod
    def Stat(self, param: str, new_value: Optional[str] = None) -> str:
        pass


class CodecFactory:

    @staticmethod
    def create_pdu_codec(MimeMap: str, Stream: bytearray, ModelName: str, SimulationTime: float) -> ICodec:
        from ncodec.pdu import PduCodec
        return PduCodec(MimeMap, Stream, ModelName, SimulationTime)

    @staticmethod
    def create_can_codec(MimeMap: str, Stream: bytearray, ModelName: str, SimulationTime: float) -> ICodec:
        from ncodec.can import CanCodec
        return CanCodec(MimeMap, Stream, ModelName, SimulationTime)

    @staticmethod
    def create_codec(MimeType: str, Stream: bytearray, ModelName: str, SimulationTime: float) -> ICodec:
        MimeMap = decode_mime_type(MimeType)
        codec_type = MimeMap.get("type")

        if codec_type == "pdu":
            return CodecFactory.create_pdu_codec(MimeMap, Stream, ModelName, SimulationTime)
        elif codec_type == "can":
            return CodecFactory.create_can_codec(MimeMap, Stream, ModelName, SimulationTime)
        else:
            raise ValueError(f"Unsupported codec type: {codec_type}")


# Export the main interfaces and factory
__all__ = [
    'ICodec',
    'CodecFactory',
    'MessageType'
]
