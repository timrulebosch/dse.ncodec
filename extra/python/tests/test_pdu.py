#!/usr/bin/env python3
"""
Test cases for PduCodec constructor
"""

import unittest
from ncodec.pdu import PduCodec, PduMessage, NCodecIpCanMessageMetadata, NCodecIpAddr, NCodecPduIpAddrV6, NCodecPduIpAddrV4, NCodecPduSocketAdapter, NCodecPduSomeIpAdapter, NCodecPduDoIpAdapter
from ncodec import TransportMetadata
from AutomotiveBus.Stream.Pdu.IpProtocol import IpProtocol
from AutomotiveBus.Stream.Pdu.IpAddr import IpAddr
from AutomotiveBus.Stream.Pdu.SocketAdapter import SocketAdapter


class TestPduCodecConstructor(unittest.TestCase):
    """Test cases for PduCodec constructor"""

    def test_pducodec_write(self):
        MimeMap={"interface":"stream","type":"pdu","schema":"fbs","swc_id":"1","ecu_id":"2"}
        codec = PduCodec(MimeMap, bytearray(), "MyModel", 0.0)
        self.assertIsNotNone(codec)
        self.assertEqual(len(codec.Stream), 0)
        pdu_write_list = [PduMessage(
            id=123,
            payload=b"Hello World This is a test message for the test case",
            swc_id=42,
            ecu_id=99,
            type=TransportMetadata.Ip,
            ip_metadata=NCodecIpCanMessageMetadata(
                eth_dst_mac=0x0000123456789ABC,
                eth_src_mac=0x0000CBA987654321,
                eth_ethertype=1,
                eth_tci_pcp=2,
                eth_tci_dei=3,
                eth_tci_vid=4,
                ip_protocol=IpProtocol.Tcp,
                ip_addr_type=IpAddr.v6,
                ip_addr=NCodecIpAddr(
                    ip_v4=None,
                    ip_v6=NCodecPduIpAddrV6(
                        src_ip=[0x2001, 0x0db8, 0xaaaa, 0x0001, 0x0000, 0x0000, 0x0000, 0x0001],  # 2001:db8:aaaa:1::1
                        dst_ip=[0x2001, 0x0db8, 0xaaaa, 0x0001, 0x0000, 0x0000, 0x0000, 0x00ff]   # 2001:db8:aaaa:1::ff
                    )
                ),
                ip_src_port=0,
                ip_dst_port=0,
                so_ad_type=SocketAdapter.some_ip,
                so_ad=NCodecPduSocketAdapter(
                    do_ip=None,
                    some_ip=NCodecPduSomeIpAdapter(
                        message_id=0x1234,       # Service ID + Method ID
                        length=16,               # Payload length + 8 byte header
                        request_id=0x5678,       # Client ID + Session ID
                        protocol_version=1,      # SOME/IP version
                        interface_version=1,     # Service interface version
                        message_type=0x00,       # REQUEST
                        return_code=0x00         # E_OK
                    )
                )
            )
        ),
        PduMessage(
            id=124,
            payload=b"Hello World This is a test message for the test case",
            swc_id=42,
            ecu_id=99,
            type=TransportMetadata.Ip,
            ip_metadata=NCodecIpCanMessageMetadata(
                eth_dst_mac=0x0000123456789ABC,
                eth_src_mac=0x0000CBA987654321,
                eth_ethertype=1,
                eth_tci_pcp=2,
                eth_tci_dei=3,
                eth_tci_vid=4,
                ip_protocol=IpProtocol.Tcp,
                ip_addr_type=IpAddr.v4,
                ip_addr=NCodecIpAddr(
                    ip_v4=NCodecPduIpAddrV4(
                        src_ip=0xC0A80101,       # 192.168.1.1
                        dst_ip=0xC0A80102        # 192.168.1.2
                    ),
                    ip_v6=None
                ),
                ip_src_port=0,
                ip_dst_port=0,
                so_ad_type=SocketAdapter.do_ip,
                so_ad=NCodecPduSocketAdapter(
                    do_ip=NCodecPduDoIpAdapter(
                        protocol_version=1,
                        payload_type=2
                    ),
                    some_ip=None
                )
            )
        )]
        codec.Write(pdu_write_list)
        codec.Flush()
        self.assertGreater(len(codec.Stream), 0)
        self.assertEqual(len(codec.Pdus), 2)
        saved_stream = bytes(codec.Stream)
        codec.Truncate()
        self.assertEqual(len(codec.Stream), 0)
        self.assertEqual(len(codec.Pdus), 0)

        codec.Stream = saved_stream
        pdu_read_list = codec.Read()
        self.assertIsNotNone(pdu_read_list)
        self.assertEqual(len(pdu_read_list), 2)
        for i, msg in enumerate(pdu_read_list):
            self.assertIsInstance(msg, PduMessage)
            self.assertEqual(msg.ecu_id, pdu_write_list[i].ecu_id)
            self.assertEqual(msg.swc_id, pdu_write_list[i].swc_id)
            self.assertEqual(msg.id, pdu_write_list[i].id)
            self.assertEqual(msg.type, pdu_write_list[i].type)
            self.assertEqual(msg.payload, pdu_write_list[i].payload)

            self.assertEqual(msg.ip_metadata.eth_dst_mac, pdu_write_list[i].ip_metadata.eth_dst_mac)
            self.assertEqual(msg.ip_metadata.eth_src_mac, pdu_write_list[i].ip_metadata.eth_src_mac)
            self.assertEqual(msg.ip_metadata.eth_tci_pcp, pdu_write_list[i].ip_metadata.eth_tci_pcp)
            self.assertEqual(msg.ip_metadata.eth_tci_vid, pdu_write_list[i].ip_metadata.eth_tci_vid)
            self.assertEqual(msg.ip_metadata.ip_addr_type, pdu_write_list[i].ip_metadata.ip_addr_type)
            self.assertEqual(msg.ip_metadata.ip_addr, pdu_write_list[i].ip_metadata.ip_addr)
            self.assertEqual(msg.ip_metadata.ip_dst_port, pdu_write_list[i].ip_metadata.ip_dst_port)
            self.assertEqual(msg.ip_metadata.ip_src_port, pdu_write_list[i].ip_metadata.ip_src_port)
            self.assertEqual(msg.ip_metadata.ip_protocol, pdu_write_list[i].ip_metadata.ip_protocol)

            self.assertEqual(msg.ip_metadata.so_ad_type, pdu_write_list[i].ip_metadata.so_ad_type)
            self.assertEqual(msg.ip_metadata.so_ad, pdu_write_list[i].ip_metadata.so_ad)
            self.assertEqual(msg.can_metadata, pdu_write_list[i].can_metadata)

if __name__ == '__main__':
    unittest.main()
