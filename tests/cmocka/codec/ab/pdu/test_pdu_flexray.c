// Copyright 2025 Robert Bosch GmbH
//
// SPDX-License-Identifier: Apache-2.0

#include <dse/testing.h>
#include <dse/logger.h>
#include <errno.h>
#include <stdio.h>
#include <dse/clib/collections/vector.h>
#include <dse/ncodec/codec.h>
#include <dse/ncodec/codec/ab/codec.h>
#include <dse/ncodec/stream/stream.h>
#include <dse/ncodec/interface/pdu.h>
#include <dse/ncodec/codec/ab/flexray/flexray.h>
#include <flexray_harness.h>


NCodecPduFlexrayConfig cc_config = {
    .bit_rate = NCodecPduFlexrayBitrate10,
    .channel_enable = NCodecPduFlexrayChannelA,
    .macrotick_per_cycle = 3361u,
    .microtick_per_cycle = 200000u,
    .network_idle_start = (3361u - 5u - 1u),
    .static_slot_length = 55u,
    .static_slot_count = 38u,
    .minislot_length = 6u,
    .minislot_count = 211u,
    .static_slot_payload_length = (32u * 2), /* Word to Byte */

    .coldstart_node = false,
    .sync_node = false,
    .coldstart_attempts = 8u,
    .wakeup_channel_select = 0, /* Channel A */
    .single_slot_enabled = false,
    .key_slot_id = 0u,
};


TestNode testnode_A = (TestNode){
    .mimetype = "application/x-automotive-bus; "                               \
        "interface=stream;type=pdu;schema=fbs;"                                \
        "ecu_id=1;vcn=2;model=flexray",
    .config = {
        .bit_rate = NCodecPduFlexrayBitrate10,
        .channel_enable = NCodecPduFlexrayChannelA,
        .macrotick_per_cycle = 3361u,
        .microtick_per_cycle = 200000u,
        .network_idle_start = (3361u - 5u - 1u),
        .static_slot_length = 55u,
        .static_slot_count = 38u,
        .minislot_length = 6u,
        .minislot_count = 211u,
        .static_slot_payload_length = (32u * 2), /* Word to Byte */
        .coldstart_node = false,
        .sync_node = false,
        .coldstart_attempts = 8u,
        .wakeup_channel_select = 0, /* Channel A */
        .single_slot_enabled = false,
        .key_slot_id = 0u,
    },
};


void vcn_2_normalactive(void** state)
{
    Mock*     mock = *state;
    TestTxRx* test = &mock->test;
    int       rc;


    *test = (TestTxRx){
        .config = {
            .node = {
                 testnode_A,
            },
            .frame_table = {
            },
        },
        .run = {
            .push_active = true,
            .steps = 1,
        },
        .expect = {
            .cycle = 0,
            .macrotick = 330,
            .poc_state = NCodecPduFlexrayPocStateNormalActive,
            .tcvr_state = NCodecPduFlexrayTransceiverStateFrameSync,
        }
    };

    flexray_harness_run_test(test);
}


void single_node__static__single_frame__tx_rx(void** state)
{
    Mock*     mock = *state;
    TestTxRx* test = &mock->test;
    int       rc;

#define PAYLOAD "hello world"
    *test = (TestTxRx){
        .config = {
            .node = {
                 testnode_A,
            },
            .frame_table = {
                { // Node 0
                    {
                        .slot_id = 7,
                        .payload_length = 64,
                        .base_cycle = 0,
                        .cycle_repetition = 1,
                        .direction = NCodecPduFlexrayDirectionTx,
                        .index = {
                            .frame_table = 0,  /* Self index. */
                        },
                    },
                    {
                        .slot_id = 7,
                        .payload_length = 64,
                        .base_cycle = 0,
                        .cycle_repetition = 1,
                        .direction = NCodecPduFlexrayDirectionRx,
                        .index = {
                            .frame_table = 1,  /* Self index. */
                        },
                    },
                },
            },
        },
        .run = {
            .push_active = true,
            .pdu = {
                {
                    .frame_config_index = 0,
                    .slot_id = 7,
                    .lpdu_status = NCodecPduFlexrayLpduStatusNotTransmitted,
                    .payload = PAYLOAD,
                    .payload_len = strlen(PAYLOAD),
                },
                {
                    .frame_config_index = 1,
                    .slot_id = 7,
                    .lpdu_status = NCodecPduFlexrayLpduStatusNotReceived,
                    .payload = PAYLOAD,
                    .payload_len = strlen(PAYLOAD),
                },
            },
            .cycles = 1,
            .steps = 2,
        },
        .expect = {
            .cycle = 0,
            .macrotick = 660,
            .poc_state = NCodecPduFlexrayPocStateNormalActive,
            .tcvr_state = NCodecPduFlexrayTransceiverStateFrameSync,
            .pdu_count = 2,
            .pdu = {
                {
                    .frame_config_index = 0,
                    .slot_id = 7,
                    .lpdu_status = NCodecPduFlexrayLpduStatusTransmitted,
                },
                {
                    .frame_config_index = 1,
                    .slot_id = 7,
                    .lpdu_status = NCodecPduFlexrayLpduStatusReceived,
                    .payload = PAYLOAD,
                    .payload_len = strlen(PAYLOAD),
                },
            },
        }
    };

    flexray_harness_run_test(test);
}


int run_pdu_flexray_tests(void)
{
    void* s = test_setup;
    void* t = test_teardown;
#define T cmocka_unit_test_setup_teardown

    const struct CMUnitTest tests[] = {
        T(vcn_2_normalactive, s, t),
        T(single_node__static__single_frame__tx_rx, s, t),
    };

    return cmocka_run_group_tests_name("PDU  FLEXRAY", tests, NULL, NULL);
}
