// This is a library for writing generators/checkers/etc

#ifndef _HIGHPLIB_H_
#define _HIGHPLIB_H_

#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "emmintrin.h"

#define MODE_BINARY 0
#define MODE_TEXT 1

#ifdef __cplusplus
extern "C" {
#endif

/////////////////////////////////////////////////////////////////////////////
// The Software is provided "AS IS" and possibly with faults. 
// Intel disclaims any and all warranties and guarantees, express, implied or
// otherwise, arising, with respect to the software delivered hereunder,
// including but not limited to the warranty of merchantability, the warranty
// of fitness for a particular purpose, and any warranty of non-infringement
// of the intellectual property rights of any third party.
// Intel neither assumes nor authorizes any person to assume for it any other
// liability. Customer will use the software at its own risk. Intel will not
// be liable to customer for any direct or indirect damages incurred in using
// the software. In no event will Intel be liable for loss of profits, loss of
// use, loss of data, business interruption, nor for punitive, incidental,
// consequential, or special damages of any kind, even if advised of
// the possibility of such damages.
//
// Copyright (c) 2003 Intel Corporation
//
// Third-party brands and names are the property of their respective owners
//
///////////////////////////////////////////////////////////////////////////
// Random Number Generation for SSE / SSE2
// Source File
// Version 0.1
// Author Kipp Owens, Rajiv Parikh
////////////////////////////////////////////////////////////////////////


void srand_sse( unsigned int seed );

void rand_sse( unsigned int* );

static __m128i cur_seed __attribute__ ((aligned (16)));

void srand_sse( unsigned int seed )
{
    cur_seed = _mm_set_epi32( seed, seed+1, seed, seed+1 );
}

inline void rand_sse( unsigned int* result )
{
    __m128i cur_seed_split __attribute__ ((aligned (16)));
    __m128i multiplier __attribute__ ((aligned (16)));
    __m128i adder __attribute__ ((aligned (16)));
    __m128i mod_mask __attribute__ ((aligned (16)));
    __m128i sra_mask __attribute__ ((aligned (16)));
    __m128i sseresult __attribute__ ((aligned (16)));
    static const unsigned int mult[4] __attribute__ ((aligned (16))) = { 214013, 17405, 214013, 69069 };
    static const unsigned int gadd[4] __attribute__ ((aligned (16))) = { 2531011, 10395331, 13737667, 1 };
    static const unsigned int mask[4]  __attribute__ ((aligned (16)))= { 0xFFFFFFFF, 0, 0xFFFFFFFF, 0 };
    static const unsigned int masklo[4]  __attribute__ ((aligned (16))) = { 0x00007FFF, 0x00007FFF, 0x00007FFF, 0x00007FFF };

    adder = _mm_load_si128( (__m128i*) gadd);
    multiplier = _mm_load_si128( (__m128i*) mult);
    mod_mask = _mm_load_si128( (__m128i*) mask);
    sra_mask = _mm_load_si128( (__m128i*) masklo);
    cur_seed_split = _mm_shuffle_epi32( cur_seed, _MM_SHUFFLE( 2, 3, 0, 1 ) );

    cur_seed = _mm_mul_epu32( cur_seed, multiplier );
    multiplier = _mm_shuffle_epi32( multiplier, _MM_SHUFFLE( 2, 3, 0, 1 ) );
    cur_seed_split = _mm_mul_epu32( cur_seed_split, multiplier );

    cur_seed = _mm_and_si128( cur_seed, mod_mask);
    cur_seed_split = _mm_and_si128( cur_seed_split, mod_mask );
    cur_seed_split = _mm_shuffle_epi32( cur_seed_split, _MM_SHUFFLE( 2, 3, 0, 1 ) );
    cur_seed = _mm_or_si128( cur_seed, cur_seed_split );
    cur_seed = _mm_add_epi32( cur_seed, adder);

    _mm_storeu_si128( (__m128i*) result, cur_seed);
    return;
}


const char* get_var(const char* name)
{
    size_t len = strlen(name);
    char env_name[len + 64];
    strcpy(env_name, "CODEHIGHP_VAR_");
    strcat(env_name, name);
    return getenv(env_name);
}

void init_gen(int mode)
{
/*  if (mode == MODE_BINARY) {
        freopen(NULL, "wb", stdout);
    }
*/
    srand(atoi(getenv("RAND_SEED")));
    srand_sse(atoi(getenv("RAND_SEED")));
}

#ifdef __cplusplus
}
#endif

#endif
