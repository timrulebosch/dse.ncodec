# Copyright 2025 Robert Bosch GmbH
# SPDX-License-Identifier: Apache-2.0

import base64
import ctypes
from ctypes import *
from typing import List
from fmpy import simulate_fmu, read_model_description, extract
from fmpy.fmi2 import FMU2Slave
from ncodec.codec_interface import CodecFactory, ICodec
from ncodec.pdu import PduMessage


# Global objects:
fmu = None
nc = None
network_rx_ref = None
network_tx_ref = None
id : c_uint32 = 0


def do_network():
    global nc
    global id

    # Fetch the stream from FMU and write to NCodec:
    stream = bytearray()
    tx_message_hex = fmu.getString([network_tx_ref])[0]
    if tx_message_hex is not None:
        stream = base64.a85decode(tx_message_hex)

    # Read messages from the NCodec:
    nc.Stream = stream
    read_pdus : List[PduMessage] = nc.Read()
    for pdus in read_pdus:
        print(f'  Received PDU from model: {pdus.id}')

    # Write messages to the NCodec:
    message = PduMessage(
        id,
        bytes([0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x07]),
        0
    )
    id += 1

    # Send the NCodec stream to FMU:
    nc.Write([message])
    nc.Flush()
    rx_message_hex = base64.a85encode(nc.Stream, adobe=False)
    rx_message_hex = rx_message_hex.decode('utf-8')
    fmu.setString([network_rx_ref], [rx_message_hex])
    nc.Truncate()


def simulation_setup():
    # Setup FMU:
    global fmu
    fmu_filename = r"fmu/example-network-fmi2.fmu"
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
    fmu.instantiate(loggingOn=True)
    fmu.setupExperiment(startTime=0.0, stopTime=4.0, tolerance=None)
    fmu.enterInitializationMode()
    fmu.exitInitializationMode()

    global nc
    nc = CodecFactory.create_codec("application/x-automotive-bus; interface=stream; type=pdu; schema=fbs; swc_id=1; ecu_id=7", bytearray(), "Test", 0.0)


def simulation_terminate():
    global fmu
    fmu.terminate()
    fmu.freeInstance()

    # global nc
    # ncodecDLL.ncodec_close(nc)


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
