<!--
Copyright 2025 Robert Bosch GmbH

SPDX-License-Identifier: Apache-2.0
-->

# Codec Example

This Codec example implements both a static and dynamic linked Codec.
It includes the following files:

```text
dse/ncodec              NCodec API source code.
└── examples/codec      Example Codec implementations.
    └── codec.c         A reference implementation of a Codec (NCodecVTable).
    └── dynamic.c       Implementation of a dynamically linked Codec.
    └── example.c       Example showing how to use the NCodec API.
    └── static.c        Implementation of a statically linked Codec.
```


## Running the Example

```bash
# Get the code.
$ git clone https://github.com/boschglobal/dse.ncodec.git
$ cd dse.ncodec

# Build (including examples).
$ make
...
$ cd dse/ncodec/build/_out/examples/codec

# Run the statically linked example.
$ bin/example_static
TRACE TX: 42 (length=11)
TRACE RX: 00 (length=37)
Message is: Hello World says simple network codec

# Run the dynamically linked example.
$ $ bin/example_dynamic lib/libcodec.so
TRACE TX: 42 (length=11)
TRACE RX: 00 (length=37)
Message is: Hello World says simple network codec
```
