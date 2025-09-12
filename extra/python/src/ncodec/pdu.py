#!/usr/bin/env python3
"""
Network Codec Module

This module provides network encoding and decoding functionality
for automotive bus schema operations.
"""

import flatbuffers
from typing import List, Optional, Dict
from dataclasses import dataclass
import ctypes
from ncodec.mimetype import decode_mime_type
from ncodec.codec_interface import ICodec
from AutomotiveBus.Stream.Pdu import (
    TransportMetadata,
    IpProtocol, 
    IpAddr,
    SocketAdapter,
    CanFrameType,
    CanMessageFormat,
    IpV4,
    IpV6,
    IpAddressV6,
    DoIpMetadata,
    SomeIpMetadata,
    IpMessageMetadata,
    Pdu,
    Stream,
    CanMessageMetadata
)

@dataclass
class NCodecPduCanMessageMetadata:
    format: CanMessageFormat.CanMessageFormat
    type: CanFrameType.CanFrameType
    interface_id: ctypes.c_uint32
    network_id: ctypes.c_uint32

@dataclass
class NCodecPduIpAddrV4:
    src_ip: ctypes.c_uint32
    dst_ip: ctypes.c_uint32

@dataclass
class NCodecPduIpAddrV6:
    src_ip: List[ctypes.c_uint16]  # 8 uint16 values
    dst_ip: List[ctypes.c_uint16]  # 8 uint16 values

@dataclass
class NCodecIpAddr:
    ip_v4: NCodecPduIpAddrV4
    ip_v6: NCodecPduIpAddrV6

@dataclass
class NCodecPduDoIpAdapter:
    protocol_version: ctypes.c_uint8
    payload_type: ctypes.c_uint16

@dataclass
class NCodecPduSomeIpAdapter:
    message_id: ctypes.c_uint32
    length: ctypes.c_uint32
    request_id: ctypes.c_uint32
    protocol_version: ctypes.c_uint8
    interface_version: ctypes.c_uint8
    message_type: ctypes.c_uint8
    return_code: ctypes.c_uint8

@dataclass
class NCodecPduSocketAdapter:
    do_ip: NCodecPduDoIpAdapter
    some_ip: NCodecPduSomeIpAdapter

@dataclass
class NCodecIpCanMessageMetadata:
    eth_dst_mac: ctypes.c_uint64
    eth_src_mac: ctypes.c_uint64
    eth_ethertype: ctypes.c_uint16
    eth_tci_pcp: ctypes.c_uint8
    eth_tci_dei: ctypes.c_uint8
    eth_tci_vid: ctypes.c_uint16
    ip_protocol: IpProtocol
    ip_addr_type: IpAddr
    ip_addr: NCodecIpAddr
    ip_src_port: ctypes.c_uint16
    ip_dst_port: ctypes.c_uint16
    so_ad_type: SocketAdapter.SocketAdapter
    so_ad: NCodecPduSocketAdapter

@dataclass
class PduMessage:
    id: ctypes.c_uint32
    payload: bytes
    type: TransportMetadata.TransportMetadata
    swc_id: ctypes.c_uint32 = 0
    ecu_id: ctypes.c_uint32 = 0
    can_metadata: NCodecPduCanMessageMetadata = None
    ip_metadata: NCodecIpCanMessageMetadata = None

class PduCodec(ICodec[PduMessage]):
    def __init__(self, MimeMap: Dict[str, str] | str, Stream: bytearray, ModelName: str, SimulationTime: float):
        # Accept MimeMap as dict, mime-type string, bytes, or None.
        if isinstance(MimeMap, str):
            # decode 'application/..; key=val' string into dict
            MimeMap_ = decode_mime_type(MimeMap)
        elif isinstance(MimeMap, Dict):
            MimeMap_ = MimeMap
        else:
            raise ValueError("Invalid MimeMap type")

        super().__init__(MimeMap_, Stream, ModelName, SimulationTime)
        self.builder = flatbuffers.Builder(1024)
        self.Pdus = []

    def emitIpAddrV4(self, msg: PduMessage) -> any:
        IpV4.Start(self.builder)
        IpV4.AddSrcAddr(self.builder, msg.ip_metadata.ip_addr.ip_v4.src_ip)
        IpV4.AddDstAddr(self.builder, msg.ip_metadata.ip_addr.ip_v4.dst_ip)
        return IpV4.End(self.builder)

    def emitIpAddrV6(self, msg: PduMessage) -> any:
        addr = msg.ip_metadata.ip_addr.ip_v6
        IpV6.Start(self.builder)
        src_addr = IpAddressV6.CreateIpAddressV6(
            self.builder,
            addr.src_ip[0], addr.src_ip[1], addr.src_ip[2], addr.src_ip[3],
            addr.src_ip[4], addr.src_ip[5], addr.src_ip[6], addr.src_ip[7]
        )
        IpV6.AddSrcAddr(self.builder, src_addr)
        dst_addr = IpAddressV6.CreateIpAddressV6(
            self.builder,
            addr.dst_ip[0], addr.dst_ip[1], addr.dst_ip[2], addr.dst_ip[3],
            addr.dst_ip[4], addr.dst_ip[5], addr.dst_ip[6], addr.dst_ip[7]
        )
        IpV6.AddDstAddr(self.builder, dst_addr)
        return IpV6.End(self.builder)

    def emitDoIpAdapter(self, msg: PduMessage) -> any:
        adapter = msg.ip_metadata.so_ad.do_ip
        DoIpMetadata.Start(self.builder)
        DoIpMetadata.AddProtocolVersion(self.builder, adapter.protocol_version)
        DoIpMetadata.AddPayloadType(self.builder, adapter.payload_type)
        return DoIpMetadata.End(self.builder)

    def emitSomeIpAdapter(self, msg: PduMessage) -> any:
        adapter = msg.ip_metadata.so_ad.some_ip
        SomeIpMetadata.Start(self.builder)
        SomeIpMetadata.AddMessageId(self.builder, adapter.message_id)
        SomeIpMetadata.AddLength(self.builder, adapter.length)
        SomeIpMetadata.AddRequestId(self.builder, adapter.request_id)
        SomeIpMetadata.AddProtocolVersion(self.builder, adapter.protocol_version)
        SomeIpMetadata.AddInterfaceVersion(self.builder, adapter.interface_version)
        SomeIpMetadata.AddMessageType(self.builder, adapter.message_type)
        SomeIpMetadata.AddReturnCode(self.builder, adapter.return_code)
        return SomeIpMetadata.End(self.builder)

    def emitIpMessageMetdata(self, msg: PduMessage) -> any:
        if msg.ip_metadata is None:
            pass

        addr_type = None
        match msg.ip_metadata.ip_addr_type:
            case IpAddr.IpAddr.v4:
                addr_type = self.emitIpAddrV4(msg)
            case IpAddr.IpAddr.v6:
                addr_type = self.emitIpAddrV6(msg)
            case IpAddr.IpAddr.NONE:
                pass

        socket_adapter = None
        match msg.ip_metadata.so_ad_type:
            case SocketAdapter.SocketAdapter.do_ip:
                socket_adapter = self.emitDoIpAdapter(msg)
            case SocketAdapter.SocketAdapter.some_ip:
                socket_adapter = self.emitSomeIpAdapter(msg)
            case _:
                pass
        
        IpMessageMetadata.Start(self.builder)
        IpMessageMetadata.AddEthDstMac(self.builder, msg.ip_metadata.eth_dst_mac)
        IpMessageMetadata.AddEthSrcMac(self.builder, msg.ip_metadata.eth_src_mac)
        IpMessageMetadata.AddEthEthertype(self.builder, msg.ip_metadata.eth_ethertype)
        IpMessageMetadata.AddEthTciPcp(self.builder, msg.ip_metadata.eth_tci_pcp)
        IpMessageMetadata.AddEthTciDei(self.builder, msg.ip_metadata.eth_tci_dei)
        IpMessageMetadata.AddEthTciVid(self.builder, msg.ip_metadata.eth_tci_vid)
        if addr_type is not None:
            IpMessageMetadata.AddIpAddrType(self.builder, msg.ip_metadata.ip_addr_type)
            IpMessageMetadata.AddIpAddr(self.builder, addr_type)
        IpMessageMetadata.AddIpProtocol(self.builder, msg.ip_metadata.ip_protocol)
        IpMessageMetadata.AddIpSrcPort(self.builder, msg.ip_metadata.ip_src_port)
        IpMessageMetadata.AddIpDstPort(self.builder, msg.ip_metadata.ip_dst_port)
        if socket_adapter is not None:
            IpMessageMetadata.AddAdapterType(self.builder, msg.ip_metadata.so_ad_type)
            IpMessageMetadata.AddAdapter(self.builder, socket_adapter)

        return IpMessageMetadata.End(self.builder)
    
    def emitCanMessageMetadata(self, msg: PduMessage) -> any:
        CanMessageMetadata.Start(self.builder)
        CanMessageMetadata.AddMessageFormat(self.builder, msg.can_metadata.format)
        CanMessageMetadata.AddFrameType(self.builder, msg.can_metadata.type)
        CanMessageMetadata.AddInterfaceId(self.builder, msg.can_metadata.interface_id)
        CanMessageMetadata.AddNetworkId(self.builder, msg.can_metadata.network_id)
        return CanMessageMetadata.End(self.builder)

    def Write(self, msgs: List[PduMessage]):
        for msg in msgs:
            transport = None
            match msg.type:
                case TransportMetadata.TransportMetadata.Can:
                    transport = self.emitCanMessageMetadata(msg)
                case TransportMetadata.TransportMetadata.Ip:
                    transport = self.emitIpMessageMetdata(msg)
                case TransportMetadata.TransportMetadata.NONE:
                    pass
                case _:
                    raise ValueError(f"Unsupported transport metadata type: {msg.type}")

            payload = self.builder.CreateByteVector(msg.payload)
            
            # Match C code: compute final IDs upfront
            swc_id = msg.swc_id if msg.swc_id != 0 else (int(self.MimeMap["swc_id"]) if "swc_id" in self.MimeMap else 0)
            ecu_id = msg.ecu_id if msg.ecu_id != 0 else (int(self.MimeMap["ecu_id"]) if "ecu_id" in self.MimeMap else 0)

            Pdu.Start(self.builder)
            Pdu.AddId(self.builder, msg.id)
            Pdu.AddPayload(self.builder, payload)
            Pdu.AddSwcId(self.builder, swc_id)
            Pdu.AddEcuId(self.builder, ecu_id)

            Pdu.AddTransportType(self.builder, msg.type)
            if transport is not None:
                Pdu.AddTransport(self.builder, transport)

            pdu = Pdu.End(self.builder)
            self.Pdus.append(pdu)

    def StreamFinalize(self) -> bytearray:
        Stream.StartPdusVector(self.builder, len(self.Pdus))
        for i in reversed(range(len(self.Pdus))):
            self.builder.PrependUOffsetTRelative(self.Pdus[i])
        pdus_vec = self.builder.EndVector(len(self.Pdus))

        Stream.Start(self.builder)
        Stream.AddPdus(self.builder, pdus_vec)
        stream = Stream.End(self.builder)
        # Finish with identifier like C code (this already includes size prefix)
        self.builder.FinishSizePrefixed(stream, b"SPDU")
        return self.builder.Output()

    def Flush(self) -> None:
        buf = self.StreamFinalize()
        if not buf:
            return
        self.Stream = bytearray(buf)
        self.builder = flatbuffers.Builder(1024)

    def decodeIpAddr(self, transport: IpMessageMetadata.IpMessageMetadata, ip_metadata: NCodecIpCanMessageMetadata):
        # Create a new table for the IP address
        ip_table = transport.IpAddr()
        # Get the IP address table from transport
        if ip_table:
            ip_metadata.ip_addr_type = transport.IpAddrType()
            if ip_metadata.ip_addr_type == IpAddr.IpAddr.v4:
                # Handle IPv4 address
                ip_v4 = IpV4.IpV4()
                ip_v4.Init(ip_table.Bytes, ip_table.Pos)
                # Initialize the IPv4 address if not already done
                if ip_metadata.ip_addr is None:
                    ip_metadata.ip_addr = NCodecIpAddr(
                        ip_v4=NCodecPduIpAddrV4(src_ip=0, dst_ip=0),
                        ip_v6=None
                    )
                # Update the IPv4 address in ip_metadata
                ip_metadata.ip_addr.ip_v4.src_ip = ip_v4.SrcAddr()
                ip_metadata.ip_addr.ip_v4.dst_ip = ip_v4.DstAddr()
            elif ip_metadata.ip_addr_type == IpAddr.IpAddr.v6:
                # Handle IPv6 address
                ip_v6 = IpV6.IpV6()
                ip_v6.Init(ip_table.Bytes, ip_table.Pos)
                # Initialize the IPv6 address if not already done
                if ip_metadata.ip_addr is None:
                    ip_metadata.ip_addr = NCodecIpAddr(
                        ip_v4=None,
                        ip_v6=NCodecPduIpAddrV6(src_ip=[0]*8, dst_ip=[0]*8)
                    )
                # Get source address
                src_addr = ip_v6.SrcAddr()
                ip_metadata.ip_addr.ip_v6.src_ip[0] = src_addr.V0()
                ip_metadata.ip_addr.ip_v6.src_ip[1] = src_addr.V1()
                ip_metadata.ip_addr.ip_v6.src_ip[2] = src_addr.V2()
                ip_metadata.ip_addr.ip_v6.src_ip[3] = src_addr.V3()
                ip_metadata.ip_addr.ip_v6.src_ip[4] = src_addr.V4()
                ip_metadata.ip_addr.ip_v6.src_ip[5] = src_addr.V5()
                ip_metadata.ip_addr.ip_v6.src_ip[6] = src_addr.V6()
                ip_metadata.ip_addr.ip_v6.src_ip[7] = src_addr.V7()
                # Get destination address
                dst_addr = ip_v6.DstAddr()
                ip_metadata.ip_addr.ip_v6.dst_ip[0] = dst_addr.V0()
                ip_metadata.ip_addr.ip_v6.dst_ip[1] = dst_addr.V1()
                ip_metadata.ip_addr.ip_v6.dst_ip[2] = dst_addr.V2()
                ip_metadata.ip_addr.ip_v6.dst_ip[3] = dst_addr.V3()
                ip_metadata.ip_addr.ip_v6.dst_ip[4] = dst_addr.V4()
                ip_metadata.ip_addr.ip_v6.dst_ip[5] = dst_addr.V5()
                ip_metadata.ip_addr.ip_v6.dst_ip[6] = dst_addr.V6()
                ip_metadata.ip_addr.ip_v6.dst_ip[7] = dst_addr.V7()

    def decodeSoAd(self, transport: IpMessageMetadata.IpMessageMetadata, ip_metadata: NCodecIpCanMessageMetadata):
        # Create a new table for the adapter
        ad_table = transport.Adapter()
        
        # Get the adapter table from transport
        if ad_table is not None:
            ip_metadata.so_ad_type = transport.AdapterType()
            if ip_metadata.so_ad_type == SocketAdapter.SocketAdapter.do_ip:
                do_ip = DoIpMetadata.DoIpMetadata()
                do_ip.Init(ad_table.Bytes, ad_table.Pos)
                ip_metadata.so_ad = NCodecPduSocketAdapter(
                    do_ip=NCodecPduDoIpAdapter(
                        protocol_version = do_ip.ProtocolVersion(),
                        payload_type = do_ip.PayloadType()
                
                    ),
                    some_ip=None
                )
            elif ip_metadata.so_ad_type == SocketAdapter.SocketAdapter.some_ip:
                # Handle SomeIP adapter
                some_ip = SomeIpMetadata.SomeIpMetadata()
                some_ip.Init(ad_table.Bytes, ad_table.Pos)
                ip_metadata.so_ad = NCodecPduSocketAdapter(
                    do_ip=None,
                    some_ip=NCodecPduSomeIpAdapter(
                        message_id=some_ip.MessageId(),
                        length=some_ip.Length(),
                        request_id=some_ip.RequestId(),
                        protocol_version = some_ip.ProtocolVersion(),
                        interface_version = some_ip.InterfaceVersion(),
                        message_type = some_ip.MessageType(),
                        return_code = some_ip.ReturnCode()
                    )
                )

    def decodeTransport(self, msg: PduMessage, pdu_obj: Pdu):
        # Get the transport table from the PDU object
        table = pdu_obj.Transport()
        if table is not None:
            transport_type = pdu_obj.TransportType()
            if transport_type == TransportMetadata.TransportMetadata.Can:
                # Decode CAN transport metadata
                can_transport = CanMessageMetadata.CanMessageMetadata()
                can_transport.Init(table.Bytes, table.Pos)
                can_metadata = NCodecPduCanMessageMetadata(
                    format=can_transport.MessageFormat(),
                    type=can_transport.FrameType(),
                    interface_id=can_transport.InterfaceId(),
                    network_id=can_transport.NetworkId()
                )
                msg.can_metadata = can_metadata
            elif transport_type == TransportMetadata.TransportMetadata.Ip:
                # Decode IP transport metadata
                ip_transport = IpMessageMetadata.IpMessageMetadata()
                ip_transport.Init(table.Bytes, table.Pos)
                ip_metadata = NCodecIpCanMessageMetadata(
                    eth_dst_mac=ip_transport.EthDstMac(),
                    eth_src_mac=ip_transport.EthSrcMac(),
                    eth_ethertype=ip_transport.EthEthertype(),
                    eth_tci_pcp=ip_transport.EthTciPcp(),
                    eth_tci_dei=ip_transport.EthTciDei(),
                    eth_tci_vid=ip_transport.EthTciVid(),
                    ip_protocol=ip_transport.IpProtocol(),
                    ip_addr_type=ip_transport.IpAddrType(),
                    ip_addr=None,  # Will be set below
                    ip_src_port=ip_transport.IpSrcPort(),
                    ip_dst_port=ip_transport.IpDstPort(),
                    so_ad_type=ip_transport.AdapterType(),
                    so_ad=None  # Will be set below
                )
                # Decode IP address
                self.decodeIpAddr(ip_transport, ip_metadata)
                # Decode Socket Adapter
                self.decodeSoAd(ip_transport, ip_metadata)
                msg.ip_metadata = ip_metadata
            else:
                # NOP for unsupported transport types
                pass

    def getStreamFromBuffer(self) -> List[Pdu.Pdu]:
        list_of_pdus = []
        if self.Stream is None or len(self.Stream) == 0:
            return []
        stream = Stream.Stream.GetRootAs(self.Stream, 4)
        for i in range(stream.PdusLength()):
            Pdu = stream.Pdus(i)
            if Pdu:
                list_of_pdus.append(Pdu)
            else:
                break
        return list_of_pdus


    def Read(self) -> List[PduMessage]:
        msgs = []
        list_of_pdus = self.getStreamFromBuffer()
        swc_id = 0
        if "swc_id" in self.MimeMap:
            swc_id = int(self.MimeMap["swc_id"])
        for pdu_obj in list_of_pdus:
            if swc_id != 0 and pdu_obj.SwcId() == swc_id:
                continue
            msg = PduMessage(
                id=pdu_obj.Id(),
                payload=pdu_obj.PayloadAsNumpy().tobytes(),
                swc_id=pdu_obj.SwcId(),
                ecu_id=pdu_obj.EcuId(),
                type=pdu_obj.TransportType()
            )
            self.decodeTransport(msg, pdu_obj)
            # If tracing is enabled
            # if hasattr(self, "trace") and self.trace is not None:
            #     self.trace.TraceRX(msg)
            msgs.append(msg)
        return msgs
    
    def Truncate(self):
        self.builder = flatbuffers.Builder(1024)
        self.Stream.clear()
        self.Pdus.clear()
    
    def Stat(self, param: str, new_value: str = None) -> str:
        if param in self.MimeMap:
            if new_value is not None:
                self.MimeMap[param] = new_value
            return self.MimeMap[param]
        elif new_value is not None:
            self.MimeMap[param] = new_value
            return self.MimeMap[param]
        return ""
