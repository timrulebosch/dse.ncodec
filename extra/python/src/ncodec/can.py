import flatbuffers
import re
from typing import Dict, List, Optional
from dataclasses import dataclass
import ctypes
from ncodec.codec_interface import ICodec
from AutomotiveBus.Stream.Frame import (
    CanFrameType,
    CanFrame,
    Frame,
    FrameTypes,
    Stream,
    Timing
)

@dataclass
class CanSender:
    bus_id: ctypes.c_uint8
    node_id: ctypes.c_uint8
    interface_id: ctypes.c_uint8

@dataclass
class CanTiming:
    send: ctypes.c_uint64
    arb: ctypes.c_uint64
    recv: ctypes.c_uint64

@dataclass
class CanMessage:
    frame_id: ctypes.c_uint32
    frame_type: CanFrameType.CanFrameType
    Sender: CanSender
    Timing: CanTiming
    Payload: bytes

class CanCodec(ICodec[CanMessage]):
    def __init__(self, MimeMap: Dict[str, str], Stream: bytearray, ModelName: str, SimulationTime: float):
        super().__init__(MimeMap, Stream, ModelName, SimulationTime)
        self.builder = flatbuffers.Builder(1024)
        self.Frames = []

    def Write(self, msgs: List[CanMessage]):
        if msgs is None or len(msgs) == 0:
            return

        for msg in msgs:
            payload = self.builder.CreateByteVector(msg.Payload)
            
            # Create CanFrame first
            CanFrame.CanFrameStart(self.builder)
            CanFrame.CanFrameAddFrameId(self.builder, msg.frame_id)
            CanFrame.CanFrameAddFrameType(self.builder, msg.frame_type)
            CanFrame.CanFrameAddPayload(self.builder, payload)
            CanFrame.CanFrameAddBusId(self.builder, msg.Sender.bus_id)
            CanFrame.CanFrameAddNodeId(self.builder, msg.Sender.node_id)
            CanFrame.CanFrameAddInterfaceId(self.builder, msg.Sender.interface_id)
            can_frame = CanFrame.CanFrameEnd(self.builder)
            
            # Now wrap it in a Frame
            Frame.FrameStart(self.builder)
            Frame.FrameAddFType(self.builder, FrameTypes.FrameTypes.CanFrame)
            Frame.FrameAddF(self.builder, can_frame)
            frame = Frame.FrameEnd(self.builder)
            
            self.Frames.append(frame)

    def StreamFinalize(self) -> bytearray:
        Stream.StartFramesVector(self.builder, len(self.Frames))
        for i in reversed(range(len(self.Frames))):
            self.builder.PrependUOffsetTRelative(self.Frames[i])
        frame_vec = self.builder.EndVector(len(self.Frames))

        Stream.Start(self.builder)
        Stream.AddFrames(self.builder, frame_vec)
        stream = Stream.End(self.builder)
        self.builder.FinishSizePrefixed(stream)

        # Return the finished bytes
        return self.builder.Output()

    def Flush(self) -> None:
        buf = self.StreamFinalize()
        self.builder = flatbuffers.Builder(1024)
        if not buf:
            return
        self.Stream = buf

    def getStreamFromBuffer(self) -> List[CanFrame.CanFrame]:
        frame_list = []
        if self.Stream is None or len(self.Stream) == 0:
            return []
        stream = Stream.Stream.GetRootAs(self.Stream, 4)
        for i in range(stream.FramesLength()):
            frame = stream.Frames(i)
            if frame and frame.FType() == FrameTypes.FrameTypes.CanFrame:
                table = frame.F()
                can_frame = CanFrame.CanFrame()
                can_frame.Init(table.Bytes, table.Pos)
                frame_list.append(can_frame)
        return frame_list

    def Read(self) -> List[CanMessage]:
        msgs = []
        list_of_frames = self.getStreamFromBuffer()
        for frame in list_of_frames:
            node_id = 0
            node_id_str = self.Stat("Node_id")
            if node_id_str:
                node_id = int(node_id_str)
            # Skip if Node_id matches frame_id (filtering logic)
            if node_id != 0 and frame.FrameId() == node_id:
                continue
            msg = CanMessage(
                frame_id=frame.FrameId(),
                frame_type=frame.FrameType(),
                Sender=CanSender(
                    bus_id=frame.BusId(),
                    node_id=frame.NodeId(),
                    interface_id=frame.InterfaceId()
                ),
                Timing=None,
                Payload=bytes(frame.PayloadAsNumpy().tobytes())
            )
            msgs.append(msg)
        return msgs

    def Truncate(self):
        self.builder = flatbuffers.Builder(1024)
        self.Stream.clear()
        self.Frames.clear()
    
    def Stat(self, param: str, new_value: str = None) -> str:
        if param in self.MimeMap:
            if new_value is not None:
                self.MimeMap[param] = new_value
            return self.MimeMap[param]
        elif new_value is not None:
            self.MimeMap[param] = new_value
            return self.MimeMap[param]
        return ""