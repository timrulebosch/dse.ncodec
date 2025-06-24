import ctypes
from ctypes import *
from fmpy import simulate_fmu, read_model_description, extract
from fmpy.fmi2 import FMU2Slave
import base64


ncodecDLL = ctypes.CDLL("lib/libncodec.so")

ncodecDLL.ncodec_open_with_stream.argtypes = [POINTER(c_char)]
ncodecDLL.ncodec_open_with_stream.restype = POINTER(c_void)

ncodecDLL.ncodec_write_can_msg.argtypes = [POINTER(c_void),c_uint32, POINTER(c_uint8), c_size_t, c_uint8]
ncodecDLL.ncodec_write_can_msg.restype = c_int64

ncodecDLL.ncodec_read_can_msg.argtypes = [POINTER(c_void), POINTER(c_uint32), POINTER(POINTER(c_uint8)), POINTER(c_size_t), POINTER(c_uint8)]
ncodecDLL.ncodec_read_can_msg.restype = c_int64

ncodecDLL.ncodec_write_stream.argtypes = [POINTER(c_void), POINTER(c_uint8), c_size_t]
ncodecDLL.ncodec_write_stream.restype = c_int64

ncodecDLL.ncodec_read_stream.argtypes = [POINTER(c_void), POINTER(POINTER(c_uint8))]
ncodecDLL.ncodec_read_stream.restype = c_size_t

ncodecDLL.ncodec_free.argtypes = [POINTER(c_uint8)]
ncodecDLL.ncodec_free.restype = None

ncodecDLL.ncodec_close.argtypes = [POINTER(c_void)]
ncodecDLL.ncodec_close.restype = None


def codec_write(message, frame_id,frame_type):
    message_len = len(message)
    # Convert Python bytes to C uint8_t array
    message_buffer = (c_uint8 * message_len)(*message)

    # Prepare output variables
    buf_ptr = POINTER(c_uint8)()
    buf_len = c_size_t()

    # Call the function
    mydll.codec_write(
        frame_id,
        frame_type,
        message_buffer,
        message_len,
        byref(buf_ptr),
        byref(buf_len)
    )

    if buf_len.value == 0 or not buf_ptr:
        print("Error: Failed to get buffer")
    else:
        # Convert to Python bytes
        buffer_data = bytes(buf_ptr[:buf_len.value])

        # Encode in ASCII85 (Base85)
        ascii85_data = base64.a85encode(buffer_data, adobe=False)  # Standard ASCII85 (not Adobe)
        # Alternative: base64.b85encode() for RFC 1924 Base85 (different encoding)

        # Print results
        print(f"Original Buffer (Hex): {' '.join(f'{x:02X}' for x in buffer_data)}")
        print(f"Original Length: {len(buffer_data)} bytes")
        print(f"ASCII85 Encoded: {ascii85_data.decode('ascii')}")
        print(f"ASCII85 Length: {len(ascii85_data)} bytes")

        # Free the allocated memory
        mydll.free_buffer(buf_ptr)
        return ascii85_data

def codec_read(message_data):
    message_len = len(message_data)
    # Convert Python bytes to C uint8_t array
    message_buffer = (c_uint8 * message_len)(*message_data)
    # Call the function
    mydll.codec_read(
        message_buffer,
        message_len
    )


# Path to your FMU file
fmu_filename = r"/path/to/fmu"
unzipdir = extract(fmu_filename)
model_desc = read_model_description(fmu_filename)

# Initialize FMU for Co-Simulation
fmu = FMU2Slave(
    guid=model_desc.guid,
    modelIdentifier=model_desc.coSimulation.modelIdentifier,
    unzipDirectory=unzipdir,
    instanceName="instance1"
)

# Instantiate FMU
fmu.instantiate()
fmu.setupExperiment(startTime=0.0, stopTime=4.0, tolerance=None)
fmu.enterInitializationMode()

# Set scalar inputs to 12
input_vars = ["M2E_Driv_WAU_switch","M2E_SIL_PSC_UBB", "M2E_SIL_UB_VR", "M2E_SIL_UB_ECU", "M2E_SIL_UB_MR"]

scalar_refs = [var.valueReference for var in model_desc.modelVariables if var.name in input_vars]
fmu.setReal(scalar_refs, [12, 12, 12, 12, 12])
fmu.exitInitializationMode()

message = bytes([0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x02, 0x07])
frame_id = 549
frame_type = 2

network_rx_var = next((var for var in model_desc.modelVariables if var.name == "network_4_1_rx"), None)

network_tx_var = next((var for var in model_desc.modelVariables if var.name == "network_4_1_tx"), None)

if network_rx_var:
    network_rx_ref = network_rx_var.valueReference
    print(f"Found network_4_1_rx with reference: {network_rx_ref}")
else:
    raise ValueError("network_4_1_rx not found in the FMU.")

if network_tx_var:
    network_tx_ref = network_tx_var.valueReference
    print(f"Found network_4_1_tx with reference: {network_tx_ref}")
else:
    raise ValueError("network_4_1_tx not found in the FMU.")

# Simulation loop (4 sec with 0.0005 step size)
step_size = 0.0005
current_time = 0.0
encoded_message = codec_write(message, frame_id, frame_type)
encoded_message = encoded_message.decode('utf-8')
while current_time < 4.0:
    # Send encoded CAN data to `network_1_1_rx`
    fmu.setReal(scalar_refs, [12, 12, 12, 12, 12])
    fmu.setString([network_rx_ref], [encoded_message])  # Send only one message at a time
    fmu.doStep(currentCommunicationPoint=current_time, communicationStepSize=step_size)
    tx_message_hex = fmu.getString([network_tx_ref])[0]  # Get hex string from FMU
    if tx_message_hex is not None:
        received_msg = base64.a85decode(tx_message_hex)
        codec_read(received_msg)
    current_time += step_size

fmu.terminate()
fmu.freeInstance()
