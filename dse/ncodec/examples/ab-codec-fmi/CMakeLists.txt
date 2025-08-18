# Copyright 2025 Robert Bosch GmbH
#
# SPDX-License-Identifier: Apache-2.0

cmake_minimum_required(VERSION 3.21)

project(AB_Codec_FMI_Example)
set(FLATCC_SOURCE_DIR  ${DSE_NCODEC_SOURCE_DIR}/schema/abs/flatcc/src)
set(FLATCC_INCLUDE_DIR ${DSE_NCODEC_SOURCE_DIR}/schema/abs/flatcc/include)
set(TARGET_NAME "ab-codec-fmi-example")
set(EXAMPLE_PATH "examples/ab-codec-fmi")

add_executable(${TARGET_NAME}
    main.c
    ncodec.c
    fmu2.c
    ${DSE_NCODEC_SOURCE_DIR}/stream/ascii85.c
    ${DSE_NCODEC_SOURCE_DIR}/stream/buffer.c
    ${DSE_NCODEC_SOURCE_DIR}/codec/ab/codec.c
    ${DSE_NCODEC_SOURCE_DIR}/codec/ab/frame_fbs.c
    ${DSE_NCODEC_SOURCE_DIR}/codec/ab/pdu_fbs.c
    ${DSE_NCODEC_SOURCE_DIR}/codec/ab/flexray/engine.c
    ${DSE_NCODEC_SOURCE_DIR}/codec/ab/flexray/fbs.c
    ${DSE_NCODEC_SOURCE_DIR}/codec/ab/flexray/state.c
    ${DSE_NCODEC_SOURCE_DIR}/codec/ab/flexray/flexray.c
    ${DSE_NCODEC_SOURCE_DIR}/codec.c
    ${FLATCC_SOURCE_DIR}/builder.c
    ${FLATCC_SOURCE_DIR}/emitter.c
    ${FLATCC_SOURCE_DIR}/refmap.c
)
target_include_directories(${TARGET_NAME}
    PRIVATE
        ${DSE_NCODEC_INCLUDE_DIR}
        ${DSE_CLIB_INCLUDE_DIR}
        ${FLATCC_INCLUDE_DIR}
)
install(TARGETS ${TARGET_NAME}
    RUNTIME DESTINATION
        ${EXAMPLE_PATH}/
)
