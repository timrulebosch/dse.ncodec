<!--
Copyright 2025 Robert Bosch GmbH

SPDX-License-Identifier: Apache-2.0
-->

# DSE NCodec Example: FMPy Integration


```bash
# Clone and build the examples.
$ git clone https://github.com/boschglobal/dse.ncodec.git
$ cd dse.ncodec
$ make

# Change to the FMPy example directory.
$ cd dse/ncodec/build/_out/examples/fmpy

# Download the FMU.
$ export FMU_URL=https://github.com/boschglobal/dse.fmi/releases/download/v1.1.28/example-network-linux-amd64-fmi2.fmu
$ curl -fSL $FMU_URL --create-dirs --output fmu/example-network-fmi2.fmu
$ ls -1shR
.:
total 8.0K
   0 fmu/
   0 lib/
8.0K simulation.py*

./fmu:
total 688K
688K example-network-fmi2.fmu*

./lib:
total 500K
500K libncodec.so*

# Run the simulation.
$ python simulation.py
```
