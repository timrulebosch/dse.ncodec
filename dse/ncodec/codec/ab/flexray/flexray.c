// Copyright 2025 Robert Bosch GmbH
//
// SPDX-License-Identifier: Apache-2.0

#include <stdbool.h>
#include <dse/logger.h>
#include <dse/ncodec/stream/stream.h>
#include <dse/ncodec/codec/ab/codec.h>
#include <dse/ncodec/codec/ab/flexray/flexray.h>



bool flexray_bus_model_consume(ABCodecBusModel* bm, NCodecPdu* pdu)
{
    FlexrayBusModel* m = (FlexrayBusModel*)bm->model;

    if (pdu->transport_type != NCodecPduTransportTypeFlexray) return false;

    ncodec_write((NCODEC*)bm->nc, pdu);
    return true;


    /*
    FIXME: consume config
    FIXME: consume status
    FIXME: consume pdus
    register_vcs_node_state(state, checks[i].vcs_n1);

    set_node_power(state, checks[i].node, true);

   

    process_config(&config_0, engine);

    shift_cycle(engine, checks[step].condition.mt,
                                checks[step].condition.cycle, true);

    set_payload(engine, config_0.node_ident.node_id,
                   frame_table_0[0].slot_id, frame_table_0[0].status,
                   (uint8_t*)PAYLOAD, strlen(PAYLOAD))
    
    */
    
    return true;
}

void Flexray_bus_model_progress(ABCodecBusModel* bm)
{
    FlexrayBusModel* m = (FlexrayBusModel*)bm->model;

    /*
    FIXME: resolve the model
    FIXME: get pdus for _this_ node.
     calculate_budget(engine, SIM_STEP_SIZE);

    for (; consume_slot(engine) == 0;) {
    }


    calculate_bus_condition(state);
    
    get_node_state(state, checks[i].node).poc_state);
    
    */
    
    // FIXME:  FlexrayState   get_node_state   release_state 
    // FIXME: any pdus to the stream.

    //     ncodec_write((NCODEC*)reader->bus_model.nc, pdu);

}

void flexray_bus_model_close(ABCodecBusModel* bm)
{
    FlexrayBusModel* m = (FlexrayBusModel*)bm->model;
    release_state(&m->state);
    release_config(&m->engine);
}

void flexray_bus_model_create(ABCodecInstance* nc)
{    
    /* Shallow copy the nc object. */
    ABCodecInstance* nc_copy = calloc(1, sizeof(ABCodecInstance));
    *nc_copy = *nc;
    nc_copy->c.stream = NULL;
    nc_copy->c.trace = (NCodecTraceVTable){0};
    nc_copy->c.private = NULL;
    nc_copy->model = NULL;
    nc_copy->fbs_builder = (flatcc_builder_t){0};
    nc_copy->fbs_builder_initalized = false;
    nc_copy->fbs_stream_initalized = false;
    nc_copy->reader = (ABCodecReader){0};

    /* Rebuild various objects in the model NC. */
    #define BUFFER_LEN    1024
    flatcc_builder_init(&nc_copy->fbs_builder);
    nc_copy->fbs_builder.buffer_flags |= flatcc_builder_with_size;
    nc_copy->fbs_stream_initalized = false;
    nc_copy->fbs_builder_initalized = true;
    nc_copy->c.stream = ncodec_buffer_stream_create(BUFFER_LEN);
 
    /* Install the duplicated NC object. */
    nc->reader.bus_model.nc = nc_copy;

    /* Install the Bus Model object. */
    FlexrayBusModel* bm = calloc(1, sizeof(FlexrayBusModel));
    bm->node_ident.node.ecu_id = nc->ecu_id;
    bm->node_ident.node.cc_id = nc->cc_id;
    bm->node_ident.node.swc_id = nc->swc_id;
    bm->engine.node_ident = bm->node_ident;

    bm->vcn_count = nc->vcn_count;
    bm->power_on = true;
    if (nc->pwr && strcmp(nc->pwr, "off")) {
        bm->power_on = false;
    }
    nc->reader.bus_model.model = bm;

    /* Configure the Bus Model VTable. */
    nc->reader.bus_model.vtable.consume = flexray_bus_model_consume;
    nc->reader.bus_model.vtable.progress = Flexray_bus_model_progress;
    nc->reader.bus_model.vtable.close = flexray_bus_model_close;
}
