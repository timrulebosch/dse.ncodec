#!/usr/bin/env python3
"""
Test cases for PduCodec constructor
"""

import unittest
from AutomotiveBus.can import *


class TestPduCodecConstructor(unittest.TestCase):
    """Test cases for PduCodec constructor"""

    def test_pducodec_write(self):
        codec = CanCodec("interface=stream;type=pdu;schema=fbs;swc_id=1;ecu_id=2", bytearray(), "MyModel", 0.0)
        self.assertIsNotNone(codec)
        self.assertEqual(len(codec.Stream), 0)
        can_write_list = [
            CanMessage(
                frame_id=1,
                frame_type=CanFrameType.CanFrameType.BaseFrame,
                Sender=CanSender(
                    bus_id=1,
                    node_id=2,
                    interface_id=3
                ),
                Timing=None,
                Payload=b'Hello'
            )
        ]
        codec.Write(can_write_list)
        codec.Flush()
        self.assertGreater(len(codec.Stream), 0)
        self.assertEqual(len(codec.Frames), 1)
        saved_stream = bytes(codec.Stream)
        codec.Truncate()
        self.assertEqual(len(codec.Stream), 0)
        self.assertEqual(len(codec.Frames), 0)

        codec.Stream = saved_stream
        can_read_list = codec.Read()
        self.assertIsNotNone(can_read_list)
        self.assertEqual(len(can_read_list), 1)
        for i, msg in enumerate(can_read_list):
            self.assertIsInstance(msg, CanMessage)
            self.assertEqual(msg.frame_id, can_write_list[i].frame_id)
            self.assertEqual(msg.frame_type, can_write_list[i].frame_type)
            self.assertEqual(msg.Payload, can_write_list[i].Payload)
            self.assertEqual(msg.Sender.bus_id, can_write_list[i].Sender.bus_id)
            self.assertEqual(msg.Sender.node_id, can_write_list[i].Sender.node_id)
            self.assertEqual(msg.Sender.interface_id, can_write_list[i].Sender.interface_id)

if __name__ == '__main__':
    unittest.main()
