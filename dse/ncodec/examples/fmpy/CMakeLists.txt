# Copyright 2025 Robert Bosch GmbH
#
# SPDX-License-Identifier: Apache-2.0

cmake_minimum_required(VERSION 3.21)


project(python_ncodec)
set(EXAMPLE_PATH "examples/fmpy")

# set(CMAKE_VERBOSE_MAKEFILE ON)
set(FLATCC_SOURCE_DIR  ${DSE_NCODEC_SOURCE_DIR}/schema/abs/flatcc/src)
set(FLATCC_INCLUDE_DIR ${DSE_NCODEC_SOURCE_DIR}/schema/abs/flatcc/include)


# Targets
# =======

# Target - NCodec
# ---------------
add_library(ncodec SHARED
    ascii85.c
    ncodec.c
    ${DSE_NCODEC_SOURCE_DIR}/stream/buffer.c
    ${DSE_NCODEC_SOURCE_DIR}/codec/ab/codec.c
    ${DSE_NCODEC_SOURCE_DIR}/codec/ab/frame_fbs.c
    ${DSE_NCODEC_SOURCE_DIR}/codec/ab/pdu_fbs.c
    ${DSE_NCODEC_SOURCE_DIR}/codec.c
    ${FLATCC_SOURCE_DIR}/builder.c
    ${FLATCC_SOURCE_DIR}/emitter.c
    ${FLATCC_SOURCE_DIR}/refmap.c
)
target_include_directories(ncodec
    PRIVATE
        ${DSE_NCODEC_INCLUDE_DIR}
        ${FLATCC_INCLUDE_DIR}
)
install(TARGETS ncodec
    LIBRARY DESTINATION
        ${EXAMPLE_PATH}/lib
    RUNTIME DESTINATION
        ${EXAMPLE_PATH}/lib
)
install(
    FILES
        simulation.py
    DESTINATION
        ${EXAMPLE_PATH}
)
