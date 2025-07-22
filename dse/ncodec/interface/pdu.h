// Copyright 2025 Robert Bosch GmbH
//
// SPDX-License-Identifier: Apache-2.0

#ifndef DSE_NCODEC_INTERFACE_PDU_H_
#define DSE_NCODEC_INTERFACE_PDU_H_

#include <stdbool.h>
#include <stdint.h>


/** NCODEC API - PDU/Stream
    =======================

    Types relating to the implementaiton of the Stream/PDU interface of
    the NCodec API.

    The root type is `NCodecPdu` which may be substitued for the `NCodecMessage`
    type when calling NCodec API methods (e.g. `ncodec_write()`).
*/


/** PDU : CAN Message/Frame Interface
    ---------------------------------
*/

typedef enum NCodecPduCanFrameFormat {
    NCodecPduCanFrameFormatBase = 0,
    NCodecPduCanFrameFormatExtended = 1,
    NCodecPduCanFrameFormatFdBase = 2,
    NCodecPduCanFrameFormatFdExtended = 3,
} NCodecPduCanFrameFormat;

typedef enum NCodecPduCanFrameType {
    NCodecPduCanFrameTypeData = 0,
    NCodecPduCanFrameTypeRemote = 1,
    NCodecPduCanFrameTypeError = 2,
    NCodecPduCanFrameTypeOverload = 3,
} NCodecPduCanFrameType;

typedef struct NCodecPduCanMessageMetadata {
    NCodecPduCanFrameFormat frame_format;
    NCodecPduCanFrameType   frame_type;
    uint32_t                interface_id;
    uint32_t                network_id;
} NCodecPduCanMessageMetadata;


/** PDU : IP Message/Frame Interface
    --------------------------------
*/

typedef enum {
    NCodecPduIpProtocolNone = 0,
    NCodecPduIpProtocolTcp = 6,
    NCodecPduIpProtocolUdp = 17,
} NCodecPduIpProtocol;

typedef enum {
    NCodecPduIpAddrNone = 0,
    NCodecPduIpAddrIPv4 = 1,
    NCodecPduIpAddrIPv6 = 2,
} NCodecPduIpAddr;

typedef enum {
    NCodecPduSoAdNone = 0,
    NCodecPduSoAdDoIP = 1,
    NCodecPduSoAdSomeIP = 2,
} NCodecPduSoAd;

typedef struct NCodecPduIpAddrV4 {
    uint32_t src_addr;
    uint32_t dst_addr;
} NCodecPduIpAddrV4;

typedef struct NCodecPduIpAddrV6 {
    uint16_t src_addr[8];
    uint16_t dst_addr[8];
} NCodecPduIpAddrV6;


typedef struct NCodecPduDoIpAdapter {
    uint8_t  protocol_version;
    uint16_t payload_type;
} NCodecPduDoIpAdapter;

typedef struct NCodecPduSomeIpAdapter {
    uint32_t message_id;
    uint32_t length;
    uint32_t request_id;
    uint8_t  protocol_version;
    uint8_t  interface_version;
    uint8_t  message_type;
    uint8_t  return_code;
} NCodecPduSomeIpAdapter;


typedef struct NCodecPduIpMessageMetadata {
    uint64_t eth_dst_mac;
    uint64_t eth_src_mac;
    uint16_t eth_ethertype;
    uint8_t  eth_tci_pcp;
    uint8_t  eth_tci_dei;
    uint16_t eth_tci_vid;

    NCodecPduIpProtocol ip_protocol;
    NCodecPduIpAddr     ip_addr_type;
    union {
        struct {
        } none;
        NCodecPduIpAddrV4 ip_v4;
        NCodecPduIpAddrV6 ip_v6;
    } ip_addr;
    uint16_t ip_src_port;
    uint16_t ip_dst_port;

    NCodecPduSoAd so_ad_type;
    union {
        struct {
        } none;
        NCodecPduDoIpAdapter   do_ip;
        NCodecPduSomeIpAdapter some_ip;
    } so_ad;
} NCodecPduIpMessageMetadata;


/** PDU : Struct Message Interface
    ------------------------------
*/

typedef struct NCodecPduStructMetadata {
    const char* type_name;
    const char* var_name;
    const char* encoding;
    uint16_t    attribute_aligned;
    bool        attribute_packed;
    const char* platform_arch;
    const char* platform_os;
    const char* platform_abi;
} NCodecPduStructMetadata;


/** PDU : FlexRay Message/Frame Interface
    -------------------------------------
*/

typedef enum {
    NCodecPduFlexrayBitrate10 = 0,
    NCodecPduFlexrayBitrate8 = 1,
    NCodecPduFlexrayBitrate5 = 2,
    NCodecPduFlexrayBitrate2_5 = 3,
} NCodecPduFlexrayBitrate;

typedef enum {
    NCodecPduFlexrayDirectionRx = 0,
    NCodecPduFlexrayDirectionTx = 1,
} NCodecPduFlexrayDirection;

typedef enum {
    NCodecPduFlexrayTransmitModeNone = 0,
    NCodecPduFlexrayTransmitModeContinuous = 1,
    NCodecPduFlexrayTransmitModeSingleShot = 2,
} NCodecPduFlexrayTransmitMode;

typedef enum {
    NCodecPduFlexrayChannelNone = 0,
    NCodecPduFlexrayChannelA = 1,
    NCodecPduFlexrayChannelB = 2,
    NCodecPduFlexrayChannelAB = 3,
} NCodecPduFlexrayChannel;

typedef enum {
    NCodecPduFlexrayChannelStatusA = 0,
    NCodecPduFlexrayChannelStatusB = 1,
    NCodecPduFlexrayChannelStatusSize = 2,
} NCodecPduFlexrayChannelStatus;

typedef enum {
    NCodecPduFlexrayTransceiverStateNoConnection = 0,
    NCodecPduFlexrayTransceiverStateNoSignal = 1,
    NCodecPduFlexrayTransceiverStateCAS = 2,
    NCodecPduFlexrayTransceiverStateWUP = 3,
    NCodecPduFlexrayTransceiverStateFrameSync = 4,
    NCodecPduFlexrayTransceiverStateFrameError = 5,
}
NCodecPduFlexrayTransceiverState;

typedef enum {
    NCodecPduFlexrayStatusPocConfig = 0,
    NCodecPduFlexrayStatusPocDefaultConfig = 1,
    NCodecPduFlexrayStatusPocHalt = 2,
    NCodecPduFlexrayStatusPocNormalActive = 3,
    NCodecPduFlexrayStatusPocNormalPassive = 4,
    NCodecPduFlexrayStatusPocReady = 5,
    NCodecPduFlexrayStatusPocStartup = 6,
    NCodecPduFlexrayStatusPocWakeup = 7,
    NCodecPduFlexrayStatusPocUndefined = 8,
} NCodecPduFlexrayPocState;

typedef enum {
    NCodecPduFlexrayCommandNotAccepted = 0,
    NCodecPduFlexrayCommandConfig = 1,
    NCodecPduFlexrayCommandReady = 2,
    NCodecPduFlexrayCommandWakeup = 3,
    NCodecPduFlexrayCommandRun = 4,
    NCodecPduFlexrayCommandAllSlots = 5,
    NCodecPduFlexrayCommandHalt = 6,
    NCodecPduFlexrayCommandFreeze = 7,
    NCodecPduFlexrayCommandAllowColdstart = 8,
} NCodecPduFlexrayPocCommand;

typedef enum {
    NCodecPduFlexrayLpduStatusTransmitted = 0,
    NCodecPduFlexrayLpduStatusTransmittedConflict = 1,
    NCodecPduFlexrayLpduStatusNotTransmitted = 2,
    NCodecPduFlexrayLpduStatusReceived = 3,
    NCodecPduFlexrayLpduStatusNotReceived = 4,
    NCodecPduFlexrayLpduStatusReceivedMoreDataAvailable = 5,
} NCodecPduFlexrayLpduStatus;

typedef struct NCodecPduFlexrayLpdu {
    uint8_t cycle; /* 0..63 */
    bool    null_frame;

    /* LPDU transmission status. */
    NCodecPduFlexrayLpduStatus status;

    /* Frame config. */
    struct {
        union {
            // FIXME are these always identical values?
            uint16_t slot_id;
            uint16_t frame_id; /* 1..2047 */
        };
        uint8_t payload_length;   /* 0..254 */
        uint8_t cycle_repetition; /* 0..63 */
        uint8_t base_cycle;       /* 0..63 */
        struct {
            uint16_t frame_config_table;
            uint16_t lpdu_table; /* Controller internal only! */
        } index;
        NCodecPduFlexrayDirection    direction;
        NCodecPduFlexrayChannel      channel;
        NCodecPduFlexrayTransmitMode transmit_mode;
    } config;
} NCodecPduFlexrayLpdu;

typedef struct NCodecPduFlexrayConfig {
    NCodecPduFlexrayBitrate bit_rate;

    /* Set according to bitrate, calculated, info only. */
    uint8_t  sample_period_ns;
    uint8_t  samples_per_microtick;
    uint8_t  microtick_ns;
    uint16_t bit_ms;

    /* User config */
    uint8_t  microtick_per_macrotick;
    uint8_t  macrotick_us;
    uint16_t macrotick_per_cycle;
    uint16_t cycle_us;
    uint32_t static_slot_count;
    uint32_t static_slot_payload_length;
    bool     single_slot_enabled; /* If true then set false by command
                                     NCodecPduFlexrayCommandAllSlots. */

    /* Modes or operation. */
    NCodecPduFlexrayTransmitMode transmit_mode;
    NCodecPduFlexrayChannel      channels_enable;

    /* Additional config, used during startup. */
    // FIXME review if necessary.
    uint8_t  key_slot_id;
    uint8_t  key_slot_id_startup;
    uint8_t  key_slot_id_sync;
    uint32_t nm_vector_length;

    /* Frame Config. */
    struct {
        NCodecPduFlexrayLpdu* table;
        size_t                count;
    } frame_config;

} NCodecPduFlexrayConfig;

typedef struct NCodecPduFlexrayStatus {
    /* Communication Cycle. */
    uint16_t macrotick;
    uint8_t  cycle;

    /* Channel Status ([0] == CH_A, [1] == CH_B). */
    struct {
        NCodecPduFlexrayTransceiverState state;
        NCodecPduFlexrayPocState         poc_state;
        /* Command interface (from controller). */
        NCodecPduFlexrayPocCommand       command;
    } channel[NCodecPduFlexrayChannelStatusSize];
} NCodecPduFlexrayStatus;

typedef enum {
    NCodecPduFlexrayMetadataTypeNone = 0,
    NCodecPduFlexrayMetadataTypeConfig = 1,
    NCodecPduFlexrayMetadataTypeStatus = 2,
    NCodecPduFlexrayMetadataTypeLpdu = 3,
} NCodecPduFlexrayMetadataType;

typedef struct NCodecPduFlexrayTransport {
    NCodecPduFlexrayMetadataType metadata_type;
    union {
        struct {
        } none;
        NCodecPduFlexrayLpdu   lpdu;
        NCodecPduFlexrayConfig config;
        NCodecPduFlexrayStatus status;
    } metadata;
} NCodecPduFlexrayTransport;

typedef enum {
    NCodecPduTransportTypeNone = 0,
    NCodecPduTransportTypeCan = 1,
    NCodecPduTransportTypeIp = 2,
    NCodecPduTransportTypeStruct = 3,
    NCodecPduTransportTypeFlexray = 4,
} NCodecPduTransportType;

typedef struct NCodecPdu {
    uint32_t       id;
    const uint8_t* payload;
    size_t         payload_len;

    /* Sender identifying properties (optional), default values are taken
       from the stream MIME Type parameters. */
    uint32_t swc_id;
    uint32_t ecu_id;

    /* Transport Metadata. */
    NCodecPduTransportType transport_type;
    union {
        struct {
        } none;
        NCodecPduCanMessageMetadata can_message;
        NCodecPduIpMessageMetadata  ip_message;
        NCodecPduStructMetadata     struct_object;
        NCodecPduFlexrayTransport   flexray;
    } transport;
} NCodecPdu;

#endif  // DSE_NCODEC_INTERFACE_PDU_H_
