// Copyright 2025 Robert Bosch GmbH
//
// SPDX-License-Identifier: Apache-2.0

#ifndef DSE_NCODEC_EXAMPLES_FLEXRAY_FLEXRAY_ANYCPU_H_
#define DSE_NCODEC_EXAMPLES_FLEXRAY_FLEXRAY_ANYCPU_H_

#include <stdint.h>
#include <dse/ncodec/interface/pdu.h>

#define FLEXRAY_CC_INDEX 0
#define FLEXRAY_CH_A     0

typedef enum {
    FrWupNone = 0,
    FrWupPowerOn = 1,
    FrWupPin = 2,
    FrWupBus = 4,
    FrWupBusAndPin = 6,
    FrWupReset = 8,
} FrWupReasonType;

typedef struct FlexrayFrameConfig {
    uint16_t slot_id;
    uint8_t  payload_length;
    uint8_t  cycle_config;
    uint16_t frame_config_table;
    uint16_t lpdu_table;

    /* These types are borrowed from interface/pdu.h */
    NCodecPduFlexrayDirection    direction;
    NCodecPduFlexrayChannel      channel;
    NCodecPduFlexrayTransmitMode transmit_mode;
} FlexrayFrameConfig;

typedef struct FlexrayControllerConfig {
    uint8_t                 cc_index;
    NCodecPduFlexrayBitrate bit_rate;

    uint8_t  microtick_per_macrotick;
    uint16_t macrotick_per_cycle;
    uint32_t static_slot_count;
    uint32_t static_slot_payload_length;
    bool     single_slot_enabled;

    NCodecPduFlexrayChannel channels_enable;

    uint32_t key_slot_id;
    uint8_t  key_slot_id_startup;
    uint8_t  key_slot_id_sync;

    uint32_t nm_vector_length;

    FlexrayFrameConfig* frame_config_table;
    size_t              frame_config_length;
} FlexrayControllerConfig;

FlexrayControllerConfig* flexray_anycpu_get_config(void);
void                     flexray_anycpu_set_wup(FrWupReasonType reason);
void                     flexray_anycpu_set_poc_state(
                        uint8_t cc, uint8_t ch, NCodecPduFlexrayPocState poc_state);
NCodecPduFlexrayPocCommand flexray_get_poc_command(uint8_t cc, uint8_t ch);
void                       flexray_anycpu_run(void);

#endif  // DSE_NCODEC_EXAMPLES_FLEXRAY_FLEXRAY_ANYCPU_H_
