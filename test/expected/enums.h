/* Generated from the Telepathy spec, version 0.1.2

Copyright (C) 2006 Collabora Limited


This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Library General Public License for more details.

*/

#ifdef __cplusplus
extern "C" {
#endif

/* A set of flags */
typedef enum {
    TP_TEST_LOWBIT = 1,
#   define TP_TEST_LOWBIT (TP_TEST_LOWBIT)
    TP_TEST_HIGHBIT = 128,
#   define TP_TEST_HIGHBIT (TP_TEST_HIGHBIT)
} TpTestFlags;

/* Adjectives which may be applied to a specification */
typedef enum {
    TP_LEVERAGING = 0,
#   define TP_LEVERAGING (TP_LEVERAGING)
    TP_SYNERGISTIC = 1,
#   define TP_SYNERGISTIC (TP_SYNERGISTIC)
} TpAdjective;



#ifdef __cplusplus
}
#endif

