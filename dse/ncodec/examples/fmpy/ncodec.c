// Copyright 2025 Robert Bosch GmbH
//
// SPDX-License-Identifier: Apache-2.0

#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <dse/platform.h>
#include <dse/ncodec/codec.h>
#include <dse/ncodec/stream/stream.h>


DLL_PUBLIC void* ncodec_open_with_stream(const char* mime_type)
{
    NCODEC* nc = ncodec_create(mime_type);
    if (nc) {
        NCodecInstance*     _nc = (NCodecInstance*)nc;
        NCodecStreamVTable* stream = ncodec_buffer_stream_create(0);
        _nc->stream = stream;
    }
    return (void*)nc;
}

DLL_PUBLIC int64_t ncodec_write_pdu_msg(
    void* nc, uint32_t id, uint8_t* payload, size_t payload_len)
{
    return ncodec_write(nc, &(struct NCodecPdu){
        .id = id,
        .payload = payload,
        .payload_len = payload_len
    });
}

DLL_PUBLIC int64_t ncodec_read_pdu_msg(void* nc,
    uint32_t* id, uint8_t** payload, size_t* payload_len)
{
    NCodecPdu msg = {};
    int64_t          rc = ncodec_read(nc, &msg);
    if (rc > 0) {
        *id = msg.id;
        *payload = malloc(msg.payload_len);
        memcpy(*payload, msg.payload, msg.payload_len);
        *payload_len = msg.payload_len;
    }
    return rc;
}

DLL_PUBLIC int64_t ncodec_write_stream(void* nc, uint8_t* buffer, size_t len)
{
    NCodecInstance* _nc = (NCodecInstance*)nc;
    if (_nc && _nc->stream && _nc->stream->write) {
        ncodec_truncate(nc);
        _nc->stream->write((NCODEC*)nc, buffer, len);
        ncodec_seek(nc, 0, NCODEC_SEEK_SET);  // Position for reading.
        return len;
    } else {
        return -ENOSTR;
    }
}

DLL_PUBLIC size_t ncodec_read_stream(void* nc, uint8_t** buffer)
{
    NCodecInstance* _nc = (NCodecInstance*)nc;
    if (_nc && _nc->stream && _nc->stream->read) {
        size_t len = ncodec_flush(nc);
        ncodec_seek(nc, 0, NCODEC_SEEK_SET);
        *buffer = malloc(len);
        return _nc->stream->read(nc, buffer, &len, NCODEC_POS_UPDATE);
    } else {
        return -ENOSTR;
    }
}

DLL_PUBLIC void ncodec_free(uint8_t* buffer)
{
    free(buffer);
}
