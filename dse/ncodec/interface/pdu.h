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


typedef enum {
    NCodecPduTransportTypeNone = 0,
    NCodecPduTransportTypeCan = 1,
    NCodecPduTransportTypeIp = 2,
    NCodecPduTransportTypeStruct = 3,
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
    } transport;
} NCodecPdu;

#endif  // DSE_NCODEC_INTERFACE_PDU_H_
