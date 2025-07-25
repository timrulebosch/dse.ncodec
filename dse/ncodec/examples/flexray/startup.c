// Copyright 2025 Robert Bosch GmbH
//
// SPDX-License-Identifier: Apache-2.0

/*
FlexRay Startup Example
=======================

FlexRay Network (Simulated)
└── Bootloader / Runnable (Leading Coldstart Node)
    └── NCodec ── FlexRay PDU Stream Interface
    └── Virtual ECU
        └── ECU API
        └── FlexRay "Any Cpu" API
└── Virtual Node (Following Coldstart Node, simulated via NCodec)
*/

#include <stdio.h>
#include <dse/ncodec/codec.h>
#include <dse/ncodec/interface/pdu.h>
#include <dse/ncodec/stream/stream.h>
#include <ecu_stub.h>
#include <flexray_anycpu.h>

#define UNUSED(x)  ((void)x)
#define BUFFER_LEN 1024

/* FlexRay Startup sequence with NCodec*/
#define MIMETYPE                                                               \
    "application/x-automotive-bus; "                                           \
    "interface=stream;type=pdu;schema=fbs;"                                    \
    "ecu_id=1;cc_id=0;swc_id=1"

static NCODEC* nc = NULL;

static void setup_ncodec(void)
{
    NCodecStreamVTable* stream = ncodec_buffer_stream_create(BUFFER_LEN);
    nc = ncodec_open(MIMETYPE, stream);
    if (nc == NULL) {
        printf("Open failed (errno %d)\n", errno);
        exit(errno);
    }

    /* Configure NCodec with 1 Virtual Coldstart Node. The virtual node
    has a slot_id (vcn_fid) of 4, the flexray_anycpu config used by this
    node has a slot_id of 2, therefore _this_ node will be the Leading
    Coldstart Node. */
    ncodec_config(nc, (struct NCodecConfigItem){ .name = "vcn", .value = "1" });
    ncodec_config(
        nc, (struct NCodecConfigItem){ .name = "vcn_fid", .value = "4" });
}

static NCodecPduFlexrayStatus get_status(void)
{
    NCodecPduFlexrayStatus fr_status = {};

    /* Search for status metadata, last one wins. */
    ncodec_seek(nc, 0, NCODEC_SEEK_SET);
    for (;;) {
        NCodecPdu pdu = {};
        if (ncodec_read(nc, &pdu) < 0) break;
        if (pdu.transport_type != NCodecPduTransportTypeFlexray ||
            pdu.transport.flexray.metadata_type ==
                NCodecPduFlexrayMetadataTypeStatus) {
            fr_status = pdu.transport.flexray.metadata.status;
        }
    }
    if (fr_status.channel[NCodecPduFlexrayChannelStatusA].state ==
        NCodecPduFlexrayTransceiverStateNoState) {
        /* The ncodec_read() did not return a status metadata block. */
        fr_status.channel[NCodecPduFlexrayChannelStatusA].poc_state =
            NCodecPduFlexrayPocStateUndefined;
    }

    /* Return status. */
    printf("Txcvr State: %d\n",
        fr_status.channel[NCodecPduFlexrayChannelStatusA].state);
    printf("POC State: %d\n",
        fr_status.channel[NCodecPduFlexrayChannelStatusA].poc_state);
    return fr_status;
}

static void push_config()
{
    FlexrayControllerConfig* config = flexray_anycpu_get_config();
    if (config == NULL) return;

    NCodecPduFlexrayLpdu* frame_table =
        calloc(config->frame_config_length, sizeof(NCodecPduFlexrayLpdu));
    for (size_t i = 0; i < config->frame_config_length; i++) {
        FlexrayFrameConfig* frame = &config->frame_config_table[i];
        frame_table[i] = (NCodecPduFlexrayLpdu){
            .config = {
                .slot_id = frame->slot_id,
                .payload_length = frame->payload_length,
                .cycle_repetition = frame->cycle_config & 0x0f,
                .base_cycle = (frame->cycle_config & 0xf0) >> 4,
                .index = {
                    .frame_config_table = i,
                    .lpdu_table = frame->lpdu_table,
                },
                .direction = frame->direction,
                .channel = frame->channel,
                .transmit_mode = frame->transmit_mode,
            },
        };
    }

    /* clang-format off */
    ncodec_write(nc, &(struct NCodecPdu){
        .transport_type = NCodecPduTransportTypeFlexray,
        .transport.flexray = {
            .metadata_type = NCodecPduFlexrayMetadataTypeConfig,
            .metadata.config = {
                .bit_rate = config->bit_rate,
                .microtick_per_macrotick = config->microtick_per_macrotick,
                .macrotick_per_cycle = config->macrotick_per_cycle,
                .static_slot_count = config->static_slot_count,
                .static_slot_payload_length = config->static_slot_payload_length,
                .single_slot_enabled = config->single_slot_enabled,
                .channels_enable = config->channels_enable,

                .key_slot_id = config->key_slot_id,
                .key_slot_id_startup = config->key_slot_id_startup,
                .key_slot_id_sync = config->key_slot_id_sync,

                .nm_vector_length = config->nm_vector_length,

                .frame_config = {
                    .table = frame_table,
                    .count = config->frame_config_length,
                },
            },
        },
    });
    /* clang-format on */
}

static void push_command(NCodecPduFlexrayPocCommand poc_cmd)
{
    if (poc_cmd == NCodecPduFlexrayCommandNone) return;
    /* clang-format off */
    ncodec_write(nc, &(struct NCodecPdu){
        .transport_type = NCodecPduTransportTypeFlexray,
        .transport.flexray = {
            .metadata_type = NCodecPduFlexrayMetadataTypeStatus,
            .metadata.status = {
                .channel[FLEXRAY_CH_A].command = poc_cmd,
            },
        },
    });
    /* clang-format on */
    printf("POC Command: %d\n", poc_cmd);
}

void do_step(double simulation_time)
{
    NCodecPduFlexrayPocCommand poc_cmd;
    NCodecPduFlexrayStatus     fr_status;

    /* Get the Flexray Bus status from NCodec. */
    fr_status = get_status();

    goto do_ecu_run;
do_ecu_run:
    /* Always truncate the NCodec object!
    Truncate when finished reading, before writing, and/or even when not using
    the NCodec object in a simulation step. */
    ncodec_truncate(nc);

    flexray_anycpu_set_poc_state(FLEXRAY_CC_INDEX, FLEXRAY_CH_A,
        fr_status.channel[NCodecPduFlexrayChannelStatusA].poc_state);
    ecu_run(simulation_time);
    flexray_anycpu_run();

    /* Process/forward any commands from the FlexRay Interface. */
    poc_cmd = flexray_get_poc_command(FLEXRAY_CC_INDEX, FLEXRAY_CH_A);
    if (poc_cmd == NCodecPduFlexrayCommandConfig) {
        push_config();
    }
    push_command(poc_cmd);

    /* Flush the NCodec object!
    Flush when finished pushing items to write those items to the underlying
    NCodec stream. A NCodec object can be flushed numerous times, each time
    the contents are appended to the underlying NCodec stream. */
    ncodec_flush(nc);
}


int main(int argc, char* argv[])
{
    UNUSED(argc);
    UNUSED(argv);

    setup_ncodec();

    double simulation_time = 0.0;
    for (int i = 0; i < 100; i++) {
        do_step(simulation_time);
        simulation_time += 0.0005;
    }

    return 0;
}
