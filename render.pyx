import numpy as np
cimport numpy as np
from libcpp.vector cimport vector
from display import palette_data

# cdef vector[int] palette_data
#
# palette_data = [0x7F7F7F, 0x2000B0, 0x2800B8, 0x6010A0,
#                 0x982078, 0xB01030, 0xA03000, 0x784000,
#                 0x485800, 0x386800, 0x386C00, 0x306040,
#                 0x305080, 0x000000, 0x000000, 0x000000,
#
#                 0xBCBCBC, 0x4060F8, 0x4040FF, 0x9040F0,
#                 0xD840C0, 0xD84060, 0xE05000, 0xC07000,
#                 0x888800, 0x50A000, 0x48A810, 0x48A068,
#                 0x4090C0, 0x000000, 0x000000, 0x000000,
#
#                 0xFFFFFF, 0x60A0FF, 0x5080FF, 0xA070FF,
#                 0xF060FF, 0xFF60B0, 0xFF7830, 0xFFA000,
#                 0xE8D020, 0x98E800, 0x70F040, 0x70E090,
#                 0x60D0E0, 0x606060, 0x000000, 0x000000,
#
#                 0xFFFFFF, 0x90D0FF, 0xA0B8FF, 0xC0B0FF,
#                 0xE0B0FF, 0xFFB8E8, 0xFFC8B8, 0xFFD8A0,
#                 0xFFF090, 0xC8F080, 0xA0F0A0, 0xA0FFC8,
#                 0xA0FFF0, 0xA0A0A0, 0x000000, 0x000000]


cdef void _render_background_cython(vector[int] pattern_tables, vector[int] name_tables, vector[int] palette, int bit4, np.ndarray[int, ndim=2] pixels):
        cdef int name_table_index, pattern_base, tile_id, pattern_tables_id, pattern1, pattern2, offset, p0, p1, shift, \
            mask, low, aid, attr, aoffset, high, index
        cdef int x, y
        name_table_index = 0  # TODO
        pattern_base = 0x1000 if bit4 else 0

        for y in range(240):
            for x in range(256):
                tile_id = (x >> 3) + (y >> 3) * 32
                pattern_tables_id = name_tables[tile_id + name_table_index * 0x400]

                pattern1 = pattern_tables_id * 16 | pattern_base
                pattern2 = pattern1 + 8 | pattern_base

                offset = y & 0x7
                p0 = pattern_tables[pattern1 + offset]
                p1 = pattern_tables[pattern2 + offset]

                shift = (~x) & 0x7
                mask = 1 << shift

                low = ((p0 & mask) >> shift) | ((p1 & mask) >> shift << 1)

                aid = (x >> 5) + (y >> 5) * 8
                attr = name_tables[name_table_index * 0x400 + aid + (32 * 30)]

                aoffset = ((x & 0x10) >> 3) | ((y & 0x10) >> 2)
                high = (attr & (3 << aoffset)) >> aoffset << 2

                index = palette[high | low]

                pixels[x, y] = palette_data[index]

def render_background_cython(vector[int] pattern_tables, vector[int] name_tables, vector[int] palette, int bit4, np.ndarray[int, ndim=2] pixels):
    _render_background_cython(pattern_tables, name_tables, palette, bit4, pixels)