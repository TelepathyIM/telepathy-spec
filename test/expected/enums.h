/* Generated from the Telepathy spec, version 0.1.2

Copyright (C) 2006 Collabora Limited


This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

*/

#ifdef __cplusplus
extern "C" {
#endif


/**
 * TpTestFlags:
 * @TP_TEST_LOWBIT:            A bit         
 * @TP_TEST_HIGHBIT:            Another bit         
 *

 * A set of flags
 *
 * Bitfield/set of flags generated from the Telepathy specification.
 */
typedef enum {
    TP_TEST_LOWBIT = 1,
    TP_TEST_HIGHBIT = 128,
} TpTestFlags;


/**
 * TpAdjective:
 * @TP_ADJECTIVE_LEVERAGING:            Can leverage synergy         
 * @TP_ADJECTIVE_SYNERGISTIC:            Can synergize with leverage         
 *

 * Adjectives which may be applied to a specification
 *
 * Enumeration generated from the Telepathy specification.
 */
/* Adjectives which may be applied to a specification */
typedef enum {
    TP_ADJECTIVE_LEVERAGING = 0,
    TP_ADJECTIVE_SYNERGISTIC = 1,
} TpAdjective;

/**
 * NUM_TP_ADJECTIVES:
 *
 * 1 higher than the highest valid value of #TpAdjective.
 */
#define NUM_TP_ADJECTIVES (1+1)



#ifdef __cplusplus
}
#endif

