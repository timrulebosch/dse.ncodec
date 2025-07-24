// Copyright 2025 Robert Bosch GmbH
//
// SPDX-License-Identifier: Apache-2.0

/*
FlexRay WUP Example
===================

FlexRay Network (Simulated)
└── Bootloader / Runnable
    └── NCodec ── FlexRay PDU Stream Interface
    └── Virtual ECU
        └── Board API
        └── ECU API
        └── FlexRay "Any Cpu" API
*/

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <dse/ncodec/codec.h>
#include <dse/ncodec/interface/pdu.h>
#include <dse/ncodec/stream/stream.h>

#define UNUSED(x)        ((void)x)
#define BUFFER_LEN       1024


/* Stub Flexray "Any Cpu" API. */
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
static void flexray_anycpu_set_wup(FrWupReasonType reason)
{
    UNUSED(reason);
}
static void flexray_anycpu_set_poc_state(int cc, int ch, int poc_state)
{
    UNUSED(cc);
    UNUSED(ch);
    UNUSED(poc_state);
}
static void flexray_anycpu_run(void)
{
}


/* Stub ECU API. */
static void ecu_run(double simulation_time)
{
    UNUSED(simulation_time);
}


/* Stub Board Control API. */
#define PIN_FR_CC0_TRCV     42
#define PIN_FR_CC0_WUP      43
#define PIN_FR_WAKEUP_EVENT 44 /* Virtual PIN. */
typedef enum {
    PowerOn = 0,
    PowerOff = 1,
} PowerState;
static bool flexray_cc_trcv_power_state = PowerOff;
static void board_set_power_state(int pin, PowerState state)
{
    switch (pin) {
    case PIN_FR_CC0_TRCV:
        flexray_cc_trcv_power_state = state;
        break;
    default:
        break;
    }
}
typedef enum {
    PinLow = 0,
    PinHigh = 1,
    PinFloat = 2,
} PinState;
static bool     board_cc0_trcv_wup_pin = PinFloat;
static bool     flexray_wup_event_pin = PinLow;
static PinState board_get_pin_state(int pin)
{
    switch (pin) {
    case PIN_FR_CC0_WUP:
        return board_cc0_trcv_wup_pin;
        break;
    default:
        return PinFloat;
    }
}
static void board_set_pin_state(int pin, PinState state)
{
    switch (pin) {
    case PIN_FR_WAKEUP_EVENT:
        flexray_wup_event_pin = state;
        break;
    default:
        break;
    }
}


/* FlexRay WUP implementation with NCodec*/
#define MIMETYPE                                                               \
    "application/x-automotive-bus; "                                           \
    "interface=stream;type=pdu;schema=fbs;"                                    \
    "ecu_id=1;cc_id=0;swc_id=1"

static NCODEC* nc = NULL;

void setup_ncodec(void)
{
    NCodecStreamVTable* stream = ncodec_buffer_stream_create(BUFFER_LEN);
    nc = ncodec_open(MIMETYPE, stream);
    if (nc == NULL) {
        printf("Open failed (errno %d)\n", errno);
        exit(errno);
    }
}

void do_step(double simulation_time)
{
    /* Power up the FlexRay transceiver of Communication Controller 0. */
    if (flexray_cc_trcv_power_state != PowerOff) {
        /* The transceiver will enter its default "power on" state and listen
        for WUP bus signals on its connected channels, or its External
        Wakeup Pin interface. */
        board_set_power_state(PIN_FR_CC0_TRCV, PowerOn);
        goto do_ecu_run;
    }

    /* Get the Flexray Bus status from NCodec. */
    NCodecPduFlexrayStatus fr_status = {};
    for (;;) {
        NCodecPdu pdu = {};
        if (ncodec_read(nc, &pdu) < 0) break;
        if (pdu.transport_type != NCodecPduTransportTypeFlexray ||
            pdu.transport.flexray.metadata_type ==
                NCodecPduFlexrayMetadataTypeStatus) {
            fr_status = pdu.transport.flexray.metadata.status;
            break;
        }
    }
    if (fr_status.channel[NCodecPduFlexrayChannelStatusA].state ==
        NCodecPduFlexrayTransceiverStateNoState) {
        /* The ncodec_read() did not return a status metadata block. */
        goto do_ecu_run;
    }

    /* Calculate WUP condition. */
    FrWupReasonType reason = FrWupNone;
    if (board_get_pin_state(PIN_FR_CC0_WUP) == PinHigh) {
        reason = FrWupPowerOn;
    }
    if (fr_status.channel[NCodecPduFlexrayChannelStatusA].state ==
        NCodecPduFlexrayTransceiverStateWUP) {
        if (reason == FrWupPowerOn) {
            reason = FrWupBusAndPin;
        } else {
            reason = FrWupBus;
        }
    }

    /* Indicate WUP condition. */
    if (reason) {
        flexray_anycpu_set_wup(reason);
        board_set_pin_state(PIN_FR_WAKEUP_EVENT, PinHigh);
    }

do_ecu_run:
    /* Always truncate the NCodec object!
    Truncate when finished reading, before writing, and/or even when not using
    the NCodec object in a simulation step. */
    ncodec_truncate(nc);

    /* Run the ECU software. The WUP event will be detected via the board
    interface and the FlexRay part (of the ECU software) will react according
    to the provided WUP reason. */
    ecu_run(simulation_time);

    /* Set the FlexRay POC State. The POC State is maintained by the NCodec and
    adjusted based on commands from the FlexRay Interface _and_ interactions
    with the FlexRay Bus (i.e. Cold Start). */
    if (fr_status.channel[NCodecPduFlexrayChannelStatusA].state ==
        NCodecPduFlexrayTransceiverStateNoState) {
        flexray_anycpu_set_poc_state(
            FLEXRAY_CC_INDEX, FLEXRAY_CH_A, NCodecPduFlexrayStatusPocUndefined);
    } else {
        flexray_anycpu_set_poc_state(FLEXRAY_CC_INDEX, FLEXRAY_CH_A,
            fr_status.channel[NCodecPduFlexrayChannelStatusA].poc_state);
    }

    /* Depending on the implementation of an ECU software, the FlexRay Interface
    may need to be explicitly run so that the FlexRay Job List is executed (if
    the appropriate conditions have been reached). The exact sequence will
    depend on the implementation. */
    flexray_anycpu_run();
}

int main(int argc, char* argv[])
{
    UNUSED(argc);
    UNUSED(argv);

    setup_ncodec();

    double simulation_time = 0.0;
    for (int i = 0; i < 10; i++) {
        do_step(simulation_time);
        simulation_time += 0.0005;
    }

    return 0;
}
