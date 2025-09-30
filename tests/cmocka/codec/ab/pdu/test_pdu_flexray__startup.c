// Copyright 2025 Robert Bosch GmbH
//
// SPDX-License-Identifier: Apache-2.0

#include <dse/testing.h>
#include <dse/logger.h>
#include <errno.h>
#include <stdio.h>
#include <dse/ncodec/codec/ab/vector.h>
#include <dse/ncodec/codec.h>
#include <dse/ncodec/codec/ab/codec.h>
#include <dse/ncodec/stream/stream.h>
#include <dse/ncodec/interface/pdu.h>
#include <dse/ncodec/codec/ab/flexray/flexray.h>
#include <flexray_harness.h>


static NCodecPduFlexrayConfig cc_config = {
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


static TestNode testnode_2vcn = (TestNode){
    .mimetype = "application/x-automotive-bus; "                               \
        "interface=stream;type=pdu;schema=fbs;"                                \
        "ecu_id=1;vcn=2;model=flexray",
    .config = {
        .node_ident.node_id = 1,
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

static TestNode testnode_0vcn = (TestNode){
    .mimetype = "application/x-automotive-bus; "                               \
        "interface=stream;type=pdu;schema=fbs;"                                \
        "ecu_id=1;model=flexray",
    .config = {
        .node_ident.node_id = 1,
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
                 testnode_2vcn,
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


static TestNode testnode_poc = (TestNode){
    .mimetype = "application/x-automotive-bus; "                               \
        "interface=stream;type=pdu;schema=fbs;"                                \
        "ecu_id=1;vcn=2;model=flexray;poca=5",
    .config = {
        .node_ident.node_id = 1,
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

void vcn_2_poc_set_normalactive(void** state)
{
    Mock*     mock = *state;
    TestTxRx* test = &mock->test;
    int       rc;

    *test = (TestTxRx){
        .config = {
            .node = {
                 testnode_poc,
            },
            .frame_table = {
            },
        },
        .run = {
            .push_active = false,
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


static TestNode testnode_bridge_sync = (TestNode){
    .mimetype = "application/x-automotive-bus; "                               \
        "interface=stream;type=pdu;schema=fbs;"                                \
        "ecu_id=2;model=flexray;bridge=sync",
    .config = {
     //   .node_ident.node_id = 2,
        .bit_rate = NCodecPduFlexrayBitrate10,
        .channel_enable = NCodecPduFlexrayChannelA,
        .coldstart_node = false,
        .sync_node = false,
        .coldstart_attempts = 8u,
        .wakeup_channel_select = 0, /* Channel A */
        .key_slot_id = 0u,
    },
};

static TestNode testnode_bridge_nonsync = (TestNode){
    .mimetype = "application/x-automotive-bus; "                               \
        "interface=stream;type=pdu;schema=fbs;"                                \
        "ecu_id=3;model=flexray;bridge=nonsync",
    .config = {
     //   .node_ident.node_id = 3,
        .bit_rate = NCodecPduFlexrayBitrate10,
        .channel_enable = NCodecPduFlexrayChannelA,
        .coldstart_node = false,
        .sync_node = false,
        .coldstart_attempts = 8u,
        .wakeup_channel_select = 0, /* Channel A */
        .key_slot_id = 0u,
    },
};


/* Bridge Mode == Sync; NCodec follows Bridge Node state. */
void bridge_sync__no_signal(void** state)
{
    Mock* mock = *state;
    skip();
}

void bridge_sync__frame_error(void** state)
{
    Mock* mock = *state;
    skip();
}

void bridge_sync__frame_sync__0vcn(void** state)
{
    /* Bridge has FrameSync, NCodec has 0 VCN, should follow Bridge. */
    Mock*     mock = *state;
    TestTxRx* test = &mock->test;
    int       rc;
    __log_level__ = LOG_DEBUG;
    *test = (TestTxRx){
        .config = {
            .node = {
                 testnode_0vcn,
                 testnode_bridge_sync,
            },
            .frame_table = {
            },
        },
        .run = {
            .push_active = true, /* Node will go to FrameError, then take sync from bridge. */
            .steps = 1,
            .bridge = {
                .set_bridge_state = true, /* Set for sync node. */
                .node_idx = 1, /* Index into config.node[] for the bridge. */
                .poc_state = NCodecPduFlexrayPocStateNormalActive,
                .tcvr_state = NCodecPduFlexrayTransceiverStateFrameSync,
            },
        },
        .expect = {
            /* Set from bridge node (sync mode). */
            .cycle = 0,
            .macrotick = 330,
            .poc_state = NCodecPduFlexrayPocStateNormalActive,
            .tcvr_state = NCodecPduFlexrayTransceiverStateFrameSync,
        }
    };

    flexray_harness_run_test(test);
}

void bridge_sync__frame_sync__delay__0vcn(void** state)
{
    // Delay bridge poc state.

    // also, node is frameerror, bus state should be sync .. but node not.
}


void bridge_nonsync__vcn_2(void** state)
{
    Mock* mock = *state;
    skip();

    // Check the bridge node state
}

void bridge_nonsync__vcn_2__push_active(void** state)
{
    Mock* mock = *state;
    skip();

    // Check the bridge node state
}


int run_pdu_flexray_startup_tests(void)
{
    void* s = test_setup;
    void* t = test_teardown;
#define T cmocka_unit_test_setup_teardown

    const struct CMUnitTest tests[] = {
        T(vcn_2_normalactive, s, t),
        T(vcn_2_poc_set_normalactive, s, t),

        T(bridge_sync__no_signal, s, t),
        T(bridge_sync__frame_error, s, t),
        T(bridge_sync__frame_sync__0vcn, s, t),


        T(bridge_nonsync__vcn_2, s, t),
        T(bridge_nonsync__vcn_2__push_active, s, t),
    };

    return cmocka_run_group_tests_name(
        "PDU  FLEXRAY::STARTUP", tests, NULL, NULL);
}
