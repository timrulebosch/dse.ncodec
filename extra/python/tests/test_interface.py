#!/usr/bin/env python3
"""
Test cases for the codec interface.

This module contains comprehensive test cases for both PduCodec and CanCodec
implementations using the common interface.
"""

import unittest
from typing import List
from ncodec.codec_interface import CodecFactory, ICodec
from ncodec.pdu import PduMessage, PduCodec
from ncodec.can import CanMessage, CanCodec, CanSender, CanTiming
# Note: Stream.Pdu and Stream.Frame modules are not present in the package; tests
# reference TransportMetadata and CanFrameType. If those live in another module,
# adjust imports accordingly. For now the tests use classes from ncodec modules.
from ncodec import TransportMetadata, CanFrameType


class TestCodecFactory(unittest.TestCase):
    """Test cases for the CodecFactory."""
    
    def test_create_pdu_codec(self):
        """Test creating a PDU codec using factory."""
        mime_map = {"interface": "stream", "type": "pdu", "schema": "fbs", "swc_id": "1", "ecu_id": "2"}
        
        codec = CodecFactory.create_pdu_codec(
            MimeMap=mime_map,
            Stream=bytearray(),
            ModelName="TestModel",
            SimulationTime=0.0
        )
        
        self.assertIsInstance(codec, PduCodec)
        self.assertEqual(codec.MimeMap, mime_map)
        self.assertEqual(codec.ModelName, "TestModel")
        self.assertEqual(codec.SimulationTime, 0.0)
    
    def test_create_can_codec(self):
        """Test creating a CAN codec using factory."""
        mime_map = {"interface": "stream", "type": "can", "schema": "fbs", "swc_id": "1", "ecu_id": "2"}
        
        codec = CodecFactory.create_can_codec(
            MimeMap=mime_map,
            Stream=bytearray(),
            ModelName="TestModel",
            SimulationTime=0.0
        )
        
        self.assertIsInstance(codec, CanCodec)
        self.assertEqual(codec.MimeMap, mime_map)
        self.assertEqual(codec.ModelName, "TestModel")
        self.assertEqual(codec.SimulationTime, 0.0)
    
    def test_create_codec_by_type_pdu(self):
        """Test creating codec by type string - PDU."""
        mime_type = "interface=stream;type=pdu;schema=fbs;swc_id=1;ecu_id=2"
        
        codec = CodecFactory.create_codec(
            MimeType=mime_type,
            Stream=bytearray(),
            ModelName="TestModel",
            SimulationTime=0.0
        )
        
        self.assertIsInstance(codec, PduCodec)
        self.assertEqual(codec.MimeMap["type"], "pdu")
        self.assertEqual(codec.MimeMap["swc_id"], "1")
    
    def test_create_codec_by_type_can(self):
        """Test creating codec by type string - CAN."""
        mime_type = "interface=stream;type=can;schema=fbs;swc_id=1;ecu_id=2"
        
        codec = CodecFactory.create_codec(
            MimeType=mime_type,
            Stream=bytearray(),
            ModelName="TestModel",
            SimulationTime=0.0
        )
        
        self.assertIsInstance(codec, CanCodec)
        self.assertEqual(codec.MimeMap["type"], "can")
        self.assertEqual(codec.MimeMap["swc_id"], "1")
    
    def test_create_codec_unsupported_type(self):
        """Test creating codec with unsupported type raises ValueError."""
        mime_type = "interface=stream;type=invalid;schema=fbs"
        
        with self.assertRaises(ValueError) as context:
            CodecFactory.create_codec(
                MimeType=mime_type,
                Stream=bytearray(),
                ModelName="TestModel",
                SimulationTime=0.0
            )
        
        self.assertIn("unsupported type: invalid", str(context.exception))


class TestInterfacePolymorphism(unittest.TestCase):
    """Test cases for polymorphic usage through the interface."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.pdu_codec = CodecFactory.create_pdu_codec(
            {"interface": "stream", "type": "pdu", "schema": "fbs", "swc_id": "1", "ecu_id": "2"},
            bytearray(),
            "TestModel",
            0.0
        )
        
        self.can_codec = CodecFactory.create_can_codec(
            {"interface": "stream", "type": "can", "schema": "fbs", "swc_id": "1", "ecu_id": "2"},
            bytearray(),
            "TestModel",
            0.0
        )
        
        self.codecs = [self.pdu_codec, self.can_codec]
    
    def test_common_interface_properties(self):
        """Test that all codecs have common interface properties."""
        for codec in self.codecs:
            self.assertIsInstance(codec.MimeMap, dict)
            self.assertEqual(codec.ModelName, "TestModel")
            self.assertEqual(codec.SimulationTime, 0.0)
            self.assertIsInstance(codec.Stream, bytearray)
    
    def test_stat_method_polymorphism(self):
        """Test Stat method works polymorphically across codecs."""
        for codec in self.codecs:
            # Set a test parameter
            codec.Stat("test_param", "test_value")
            
            # Get the parameter back
            value = codec.Stat("test_param")
            self.assertEqual(value, "test_value")
    
    def test_truncate_method_polymorphism(self):
        """Test Truncate method works polymorphically across codecs."""
        for codec in self.codecs:
            # Should not raise any exceptions
            codec.Truncate()
            
            # Stream should be reset
            self.assertEqual(len(codec.Stream), 0)


class TestPduOperations(unittest.TestCase):
    """Test cases for PDU-specific operations."""
    
    def setUp(self):
        """Set up PDU codec for testing."""
        self.codec = PduCodec(
            MimeMap={"interface": "stream", "type": "pdu", "schema": "fbs", "swc_id": "1", "ecu_id": "2"},
            Stream=bytearray(),
            ModelName="PDUModel",
            SimulationTime=1.0
        )
        
        self.test_message = PduMessage(
            id=1,
            payload=b"Hello PDU",
            type=TransportMetadata.NONE,
            swc_id=100,
            ecu_id=200
        )
    
    def test_write_single_message(self):
        """Test writing a single PDU message."""
        initial_stream_size = len(self.codec.Stream)
        
        self.codec.Write([self.test_message])
        
        # Stream size should not change until flush
        self.assertEqual(len(self.codec.Stream), initial_stream_size)
    
    def test_write_and_flush(self):
        """Test writing and flushing PDU messages."""
        self.codec.Write([self.test_message])
        self.codec.Flush()
        
        # Stream should have data after flush
        self.assertGreater(len(self.codec.Stream), 0)
    
    def test_write_flush_read_cycle(self):
        """Test complete write-flush-read cycle for PDU."""
        # Write message
        self.codec.Write([self.test_message])
        self.codec.Flush()
        
        # Read back
        decoded_messages = self.codec.Read()
        
        # Verify we got our message back
        self.assertEqual(len(decoded_messages), 1)
        decoded_msg = decoded_messages[0]
        
        self.assertEqual(decoded_msg.id, self.test_message.id)
        self.assertEqual(decoded_msg.payload, self.test_message.payload)
        self.assertEqual(decoded_msg.swc_id, self.test_message.swc_id)
        self.assertEqual(decoded_msg.ecu_id, self.test_message.ecu_id)
    
    def test_write_multiple_messages(self):
        """Test writing multiple PDU messages."""
        messages = [
            PduMessage(id=1, payload=b"Message 1", type=TransportMetadata.NONE),
            PduMessage(id=2, payload=b"Message 2", type=TransportMetadata.NONE),
            PduMessage(id=3, payload=b"Message 3", type=TransportMetadata.NONE)
        ]
        
        self.codec.Write(messages)
        self.codec.Flush()

        self.codec.Stat("swc_id", "2")
        decoded_messages = self.codec.Read()
        self.assertEqual(len(decoded_messages), 3)
        
        for i, decoded_msg in enumerate(decoded_messages):
            self.assertEqual(decoded_msg.id, messages[i].id)
            self.assertEqual(decoded_msg.payload, messages[i].payload)
    
    def test_stream_finalize(self):
        """Test StreamFinalize method returns serialized data."""
        self.codec.Write([self.test_message])
        
        stream_data = self.codec.StreamFinalize()
        
        self.assertIsInstance(stream_data, bytearray)
        self.assertGreater(len(stream_data), 0)
    
    def test_truncate_clears_state(self):
        """Test that Truncate clears codec state."""
        self.codec.Write([self.test_message])
        self.codec.Flush()
        
        # Verify we have data
        self.assertGreater(len(self.codec.Stream), 0)
        
        # Truncate
        self.codec.Truncate()
        
        # Verify state is cleared
        self.assertEqual(len(self.codec.Stream), 0)


class TestCanOperations(unittest.TestCase):
    """Test cases for CAN-specific operations."""
    
    def setUp(self):
        """Set up CAN codec for testing."""
        self.codec = CanCodec(
            MimeMap={"interface": "stream", "type": "can", "schema": "fbs", "swc_id": "1", "ecu_id": "2"},
            Stream=bytearray(),
            ModelName="CANModel",
            SimulationTime=2.0
        )
        
        self.test_message = CanMessage(
            frame_id=0x123,
            frame_type=CanFrameType.BaseFrame,
            Sender=CanSender(bus_id=1, node_id=2, interface_id=3),
            Timing=None,
            Payload=b"Hello CAN"
        )
    
    def test_write_single_message(self):
        """Test writing a single CAN message."""
        initial_stream_size = len(self.codec.Stream)
        
        self.codec.Write([self.test_message])
        
        # Stream size should not change until flush
        self.assertEqual(len(self.codec.Stream), initial_stream_size)
    
    def test_write_and_flush(self):
        """Test writing and flushing CAN messages."""
        self.codec.Write([self.test_message])
        self.codec.Flush()
        
        # Stream should have data after flush
        self.assertGreater(len(self.codec.Stream), 0)
    
    def test_write_flush_read_cycle(self):
        """Test complete write-flush-read cycle for CAN."""
        # Write message
        self.codec.Write([self.test_message])
        self.codec.Flush()
        
        # Read back
        decoded_messages = self.codec.Read()
        
        # Verify we got our message back
        self.assertEqual(len(decoded_messages), 1)
        decoded_msg = decoded_messages[0]
        
        self.assertEqual(decoded_msg.frame_id, self.test_message.frame_id)
        self.assertEqual(decoded_msg.frame_type, self.test_message.frame_type)
        self.assertEqual(decoded_msg.Payload, self.test_message.Payload)
        self.assertEqual(decoded_msg.Sender.bus_id, self.test_message.Sender.bus_id)
    
    def test_stream_finalize(self):
        """Test StreamFinalize method returns serialized data."""
        self.codec.Write([self.test_message])
        
        stream_data = self.codec.StreamFinalize()
        
        self.assertIsInstance(stream_data, bytearray)
        self.assertGreater(len(stream_data), 0)
    
    def test_truncate_clears_state(self):
        """Test that Truncate clears codec state."""
        self.codec.Write([self.test_message])
        self.codec.Flush()
        
        # Verify we have data
        self.assertGreater(len(self.codec.Stream), 0)
        
        # Truncate
        self.codec.Truncate()
        
        # Verify state is cleared
        self.assertEqual(len(self.codec.Stream), 0)


class TestGenericOperations(unittest.TestCase):
    """Test cases for generic operations using the interface."""
    
    def generic_codec_test(self, codec: ICodec, test_message):
        """Generic test function that works with any codec."""
        # Write message
        codec.Write([test_message])
        
        # Get finalized stream
        stream_data = codec.StreamFinalize()
        self.assertIsInstance(stream_data, bytearray)
        self.assertGreater(len(stream_data), 0)
        
        # Flush to make data available
        codec.Flush()
        self.assertGreater(len(codec.Stream), 0)
        
        # Read back
        codec.Stat("swc_id", "2")
        decoded = codec.Read()
        self.assertEqual(len(decoded), 1)
        
        # Truncate for cleanup
        codec.Truncate()
        self.assertEqual(len(codec.Stream), 0)
    
    def test_generic_pdu_operations(self):
        """Test generic operations with PDU codec."""
        codec = CodecFactory.create_pdu_codec(
            {"interface": "stream", "type": "pdu", "schema": "fbs", "swc_id": "1", "ecu_id": "2"},
            bytearray(),
            "GenericModel",
            0.0
        )
        
        message = PduMessage(
            id=42,
            payload=b"Generic PDU",
            type=TransportMetadata.NONE
        )
        
        self.generic_codec_test(codec, message)
    
    def test_generic_can_operations(self):
        """Test generic operations with CAN codec."""
        codec = CodecFactory.create_can_codec(
            {"interface": "stream", "type": "can", "schema": "fbs", "swc_id": "1", "ecu_id": "2"},
            bytearray(),
            "GenericModel",
            0.0
        )
        
        message = CanMessage(
            frame_id=0x456,
            frame_type=CanFrameType.BaseFrame,
            Sender=CanSender(bus_id=1, node_id=1, interface_id=1),
            Timing=None,
            Payload=b"Generic CAN"
        )
        
        self.generic_codec_test(codec, message)
    
    def test_batch_operations_multiple_codecs(self):
        """Test batch operations across multiple codec types."""
        codecs = [
            CodecFactory.create_pdu_codec(
                {"interface": "stream", "type": "pdu", "schema": "fbs", "swc_id": "1", "ecu_id": "2"},
                bytearray(),
                "BatchModel",
                0.0
            ),
            CodecFactory.create_can_codec(
                {"interface": "stream", "type": "can", "schema": "fbs", "swc_id": "1", "ecu_id": "2"},
                bytearray(),
                "BatchModel",
                0.0
            )
        ]
        
        for i, codec in enumerate(codecs):
            # Test that all codecs support the interface
            self.assertIsInstance(codec, ICodec)
            
            # Test common properties
            self.assertEqual(codec.ModelName, "BatchModel")
            self.assertEqual(codec.SimulationTime, 0.0)
            
            # Test parameter setting
            codec.Stat(f"test_param_{i}", f"test_value_{i}")
            value = codec.Stat(f"test_param_{i}")
            self.assertEqual(value, f"test_value_{i}")


class TestErrorHandling(unittest.TestCase):
    """Test cases for error handling in the codec interface."""
    
    def test_invalid_mime_type_format(self):
        """Test handling of invalid MIME type format."""
        with self.assertRaises(ValueError):
            CodecFactory.create_codec(
                MimeType="invalid_format_no_equals",
                Stream=bytearray(),
                ModelName="TestModel",
                SimulationTime=0.0
            )
    
    def test_empty_message_list(self):
        """Test handling of empty message lists."""
        codec = CodecFactory.create_pdu_codec(
            {"interface": "stream", "type": "pdu", "schema": "fbs"},
            bytearray(),
            "TestModel",
            0.0
        )
        
        # Should not raise an exception
        codec.Write([])
        codec.Flush()
        
        decoded = codec.Read()
        self.assertEqual(len(decoded), 0)
    
    def test_read_without_write(self):
        """Test reading without writing anything."""
        codec = CodecFactory.create_pdu_codec(
            {"interface": "stream", "type": "pdu", "schema": "fbs"},
            bytearray(),
            "TestModel",
            0.0
        )
        
        decoded = codec.Read()
        self.assertEqual(len(decoded), 0)


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2)