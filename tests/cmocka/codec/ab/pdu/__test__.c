// Copyright 2025 Robert Bosch GmbH
//
// SPDX-License-Identifier: Apache-2.0

#include <dse/testing.h>

extern int run_pdu_tests(void);
extern int run_pdu_can_tests(void);
extern int run_pdu_ip_tests(void);
extern int run_pdu_struct_tests(void);

int main()
{
    int rc = 0;
    rc |= run_pdu_tests();
    rc |= run_pdu_can_tests();
    rc |= run_pdu_ip_tests();
    rc |= run_pdu_struct_tests();
    return rc;
}
