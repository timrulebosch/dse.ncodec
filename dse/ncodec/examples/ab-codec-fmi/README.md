<!--
Copyright 2025 Robert Bosch GmbH

SPDX-License-Identifier: Apache-2.0
-->

# AB Codec with PDU Stream and FMI 2 String Variables

This example demonstrates how to do a basis integration of the Automotive Bus
(AB) Codec with an FMU Importer supporting FMI 2 String Variables.

It includes the following files:

```text
dse/ncodec                 NCodec API source code.
└── examples/ab-codec-fmi  AB Codec basis integration for FMI 2.
    └── CMakeLists.txt     Makefile listing required objects.
    └── fmu2.c             Mock implementation of an FMI 2 FMU.
    └── ncodec.c           NCodec integration with trace support.
    └── main.c             Example with simplified importer.
```


## Running the Example

```bash
# Get the code.
$ git clone https://github.com/boschglobal/dse.ncodec.git
$ cd dse.ncodec

# Build (including examples).
$ make

# Run the example.
$ dse/ncodec/build/_out/examples/ab-codec-fmi/ab-codec-fmi-example
TRACE TX: 42 (length=11)
BUFFER TX: (86)
ASCII85 TX: (104) ;?-[s#QOi);c#k^]`8$3"98E%!<<*""98E%h#IES...
TRACE RX: 42 (length=11)
TRACE TX: 24 (length=11)
ASCII85 RX: (104) ;?-[s#QOi);c#k^]`8$3"98E%!<<*""98E%h#IES...
BUFFER RX: (86)
TRACE RX: 24 (length=11)
Message is: Hello World
```
