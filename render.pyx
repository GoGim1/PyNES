import numpy as np
from display import palette_data
cimport numpy as np
cimport cython

@cython.boundscheck(False)
@cython.wraparound(False)
def render_background_cython(pattern_tables, name_tables, palette, bit4, pixels):
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

                index = high | low

                pixels[x, y] = palette_data[palette[index]]