# Copyright 2025 Robert Bosch GmbH
# SPDX-License-Identifier: Apache-2.0

import base64
import ctypes
from ctypes import *
from fmpy import simulate_fmu, read_model_description, extract
from fmpy.fmi2 import FMU2Slave


# Global objects:
fmu = None
nc = None
network_rx_ref = None
network_tx_ref = None


# Setup the NCodec DLL:
ncodecDLL = ctypes.CDLL("lib/libncodec.so")
ncodecDLL.ncodec_open_with_stream.argtypes = [POINTER(c_char)]
ncodecDLL.ncodec_open_with_stream.restype = c_void_p
ncodecDLL.ncodec_write_pdu_msg.argtypes = [c_void_p,c_uint32, POINTER(c_uint8), c_size_t]
ncodecDLL.ncodec_write_pdu_msg.restype = c_int64
ncodecDLL.ncodec_read_pdu_msg.argtypes = [c_void_p, POINTER(c_uint32), POINTER(POINTER(c_uint8)), POINTER(c_size_t)]
ncodecDLL.ncodec_read_pdu_msg.restype = c_int64
ncodecDLL.ncodec_write_stream.argtypes = [c_void_p, POINTER(c_uint8), c_size_t]
ncodecDLL.ncodec_write_stream.restype = c_int64
ncodecDLL.ncodec_read_stream.argtypes = [c_void_p, POINTER(POINTER(c_uint8))]
ncodecDLL.ncodec_read_stream.restype = c_size_t
ncodecDLL.ncodec_free.argtypes = [POINTER(c_uint8)]
ncodecDLL.ncodec_free.restype = None
ncodecDLL.ncodec_close.argtypes = [c_void_p]
ncodecDLL.ncodec_close.restype = None


def do_network():
    global nc

    # Fetch the stream from FMU and write to NCodec:
    stream = bytes()
    tx_message_hex = fmu.getString([network_tx_ref])[0]
    if tx_message_hex is not None:
        stream = base64.a85decode(tx_message_hex)
    stream_len = len(stream)
    ncodecDLL.ncodec_write_stream(nc, (c_uint8 * stream_len)(*stream), len(stream_len))

    # Read messages from the NCodec:
    id = c_uint32()
    payload = POINTER(c_uint8)()
    payload_len = c_size_t()
    rc = ncodecDLL.ncodec_read_pdu_msg(nc, byref(id), byref(payload), byref(payload_len))
    print(f"FMU Tx ({id}): {' '.join(f'{x:02X}' for x in payload)} (len={payload_len})")
    # TODO while loop rc > 0
    ncodecDLL.ncodec_free(payload)

    # Write messages to the NCodec:
    message = bytes([0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x07])
    message_len = len(message)
    ncodecDLL.ncodec_write_pdu_msg(nc, 549, (c_uint8 * message_len)(*message), message_len, 2)

    # Send the NCOdec stream to FMU:
    stream = POINTER(c_uint8)()
    stream_len = ncodecDLL.ncodec_read_stream(nc, stream)
    rx_message_hex = bytes(stream[:stream_len.value])
    rx_message_hex = base64.a85encode(rx_message_hex, adobe=False)
    rx_message_hex = stream.decode('utf-8')
    fmu.setString([network_rx_ref], [rx_message_hex])
    ncodecDLL.ncodec_free(stream)


def simulation_setup():
    # Setup FMU:
    global fmu
    unzipdir = extract(r"fmu/example-network-fmi2.fmu")
    model_desc = read_model_description(fmu_filename)
    fmu = FMU2Slave(
        guid=model_desc.guid,
        modelIdentifier=model_desc.coSimulation.modelIdentifier,
        unzipDirectory=unzipdir,
        instanceName="network"
    )

    # Locate network variables
    global network_rx_ref
    global network_tx_ref
    network_rx_var = next((var for var in model_desc.modelVariables if var.name == "pdu_rx"), None)
    network_tx_var = next((var for var in model_desc.modelVariables if var.name == "pdu_tx"), None)
    if network_rx_var:
        network_rx_ref = network_rx_var.valueReference
    else:
        raise ValueError("pdu_rx not found in the FMU.")
    if network_tx_var:
        network_tx_ref = network_tx_var.valueReference
    else:
        raise ValueError("pdu_tx not found in the FMU.")


def simulation_instantiate():
    global fmu
    fmu.instantiate()
    fmu.setupExperiment(startTime=0.0, stopTime=4.0, tolerance=None)
    fmu.enterInitializationMode()
    fmu.exitInitializationMode()

    global nc
    nc = ncodecDLL.ncodec_open_with_stream("application/x-automotive-bus; interface=stream; type=pdu; schema=fbs; swc_id=23; ecu_id=5")


def simulation_terminate():
    global fmu
    fmu.terminate()
    fmu.freeInstance()

    global nc
    ncodecDLL.ncodec_close(nc)


# Run the simulation
simulation_setup()
simulation_instantiate()

step_size = 0.0005
current_time = 0.0
while current_time < 4.0:
    do_network()
    fmu.doStep(currentCommunicationPoint=current_time, communicationStepSize=step_size)
    current_time += step_size

simulation_terminate()
