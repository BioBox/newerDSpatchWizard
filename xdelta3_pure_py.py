"""
Newer Super Mario Bros. DS Patch Wizard ("Newer DS Patch Wizard")
Copyright (C) 2017 RoadrunnerWMC, skawo

This file is part of Newer DS Patch Wizard.
"""
COPYRIGHT = """
Newer DS Patch Wizard is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Newer DS Patch Wizard is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Newer DS Patch Wizard.  If not, see <http://www.gnu.org/licenses/>.
"""
COPYRIGHT_HTML = """
Newer DS Patch Wizard is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
<br><br>
Newer DS Patch Wizard is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
<br><br>
You should have received a copy of the GNU General Public License
along with Newer DS Patch Wizard.  If not, see
<a href="http://www.gnu.org/licenses/">http://www.gnu.org/licenses/</a>.
"""

import collections
import io
import lzma
import os
from typing import BinaryIO, List, Optional, Type
import zlib  # for adler32()


# RFC 3284 (VCDIFF): https://datatracker.ietf.org/doc/html/rfc3284


# xdelta3 extends the VCDIFF format in a few ways. Since I couldn't find
# any existing documentation on this other than xdelta3's source code,
# here's an explanation:
# - If bit 2 (VCD_APPHEADER) of Hdr_Indicator is non-zero, this
#   indicates that an application-specific header is included. It is an
#   integer-length-prefixed blob that comes after the optional custom
#   code table, and has no guaranteed internal structure.
# - If bit 2 (VCD_ADLER32) of Win_Indicator is non-zero, this indicates
#   that the Adler-32 checksum of the target window is included in the
#   window header, to allow the decoder to verify that the output is
#   correct. It comes right after the "Length of addresses for COPYs"
#   value, is exactly four bytes long (not a variable-length integer),
#   and is in big-endian (i.e. most-significant byte first).
# - The RFC does not specify any secondary compression IDs. xdelta3
#   uses the following IDs:
#   - 1 = DJW
#   - 2 = LZMA
#   - 16 = FGK


VCD_DECOMPRESS = 1
VCD_CODETABLE = 2
VCD_APPHEADER = 4  # xdelta3 custom extension to VCDIFF format

VCD_SOURCE = 1
VCD_TARGET = 2
VCD_ADLER32 = 4  # xdelta3 custom extension to VCDIFF format

VCD_SELF = 0
VCD_HERE = 1

VCD_DATACOMP = 1
VCD_INSTCOMP = 2
VCD_ADDRCOMP = 4

# Compression format IDs used by xdelta3 (not defined in RFC 3284)
VCD_COMPRESSION_DJW = 1
VCD_COMPRESSION_LZMA = 2
VCD_COMPRESSION_FGK = 16

DEFAULT_S_NEAR = 4
DEFAULT_S_SAME = 3

INST_TYPE_ADD = 1
INST_TYPE_RUN = 2
INST_TYPE_COPY = 3


def get_file_len(file: BinaryIO) -> int:
    """Helper to get the total length of a file-like object"""
    pos = file.tell()
    file.seek(0, os.SEEK_END)
    end = file.tell()
    file.seek(pos)
    return end


def read_vcdiff_integer(file: BinaryIO) -> int:
    """
    Read a variable-length VCDIFF integer. See RFC 3284, section 2.
    """
    value = 0
    for _ in range(99):
        this_byte = file.read(1)[0]

        value <<= 7
        value |= this_byte & 0x7f

        if not (this_byte & 0x80):
            return value

    raise ValueError('Variable-length integer never ended')


class AbstractXdeltaDecompressor:
    """
    Superclass for classes that are able to decompress "secondary
    compression" formats.

    One of these is created per data stream per file -- i.e. one for
    adds/runs data, one for instructions data, and one for addresses
    data. So three per VCDIFF file, total. These are used across ALL
    windows in a VCDIFF file. This is important because only the first
    window has stream headers!
    """
    def decompress_chunk(self, data: bytes) -> bytes:
        """Decompress one window's worth of data"""
        raise NotImplementedError


class XdeltaNullDecompressor(AbstractXdeltaDecompressor):
    """
    Class implementing the AbstractXdeltaDecompressor interface, but
    without decompressing anything
    """
    def decompress_chunk(self, data: bytes) -> bytes:
        """Decompress one window's worth of data"""
        return data


class XdeltaLZMADecompressor(AbstractXdeltaDecompressor):
    """
    Class implementing the AbstractXdeltaDecompressor interface for LZMA
    compression
    """
    def __init__(self):
        self._decomp = lzma.LZMADecompressor()

    def decompress_chunk(self, data: bytes) -> bytes:
        """Decompress one window's worth of data"""
        f = io.BytesIO(data)
        decomp_size = read_vcdiff_integer(f)
        decomp = self._decomp.decompress(memoryview(data)[f.tell():])
        if len(decomp) != decomp_size:
            raise ValueError(f'LZMA: expected decompressed size {decomp_size}, found {len(decomp)}')
        return decomp


class XdeltaDecompressorTriple:
    """
    Container for three decompressors (one per data stream for a VCDIFF
    file)
    """
    adds_runs: AbstractXdeltaDecompressor
    instructions: AbstractXdeltaDecompressor
    addresses: AbstractXdeltaDecompressor

    def __init__(self, adds_runs, instructions, addresses):
        super().__init__()
        self.adds_runs = adds_runs
        self.instructions = instructions
        self.addresses = addresses

    @classmethod
    def build_from_decompressor_value(cls,
            value: Optional[int]) -> 'XdeltaDecompressorTriple':
        """Build an instance from a secondary-compressor-ID value"""
        if value is None:
            return cls.build_from_decompressor_class(XdeltaNullDecompressor)
        elif value == VCD_COMPRESSION_LZMA:
            return cls.build_from_decompressor_class(XdeltaLZMADecompressor)
        else:
            raise NotImplementedError(f'Unsupported secondary compression type: {value}')

    @classmethod
    def build_from_decompressor_class(cls,
            decomp_cls: Type[AbstractXdeltaDecompressor]) -> 'XdeltaDecompressorTriple':
        """Build an instance from an AbstractXdeltaDecompressor subclass"""
        return cls(decomp_cls(), decomp_cls(), decomp_cls())


Instruction = collections.namedtuple('Instruction', 'type size mode')
# type: INST_TYPE_ADD, etc
# size: int
# mode: int


class VCDIFFCodeTable:
    """RFC 3284, section 5.6"""
    s_near: int
    s_same: int
    # Instead of including nops, we just make some lists one element long
    i_code: List[List[Instruction]]

    @classmethod
    def build_default(cls) -> 'VCDIFFCodeTable':
        """Build the default code table"""

        code_table = []

        # (Row numbers from RFC 3284, section 5.6)

        # 1.
        code_table.append([Instruction(INST_TYPE_RUN, 0, 0)])

        # 2.
        for size in range(18):
            code_table.append([Instruction(INST_TYPE_ADD, size, 0)])

        # 3. - 11.
        for mode in range(9):
            code_table.append([Instruction(INST_TYPE_COPY, 0, mode)])
            for size in range(4, 19):
                code_table.append([Instruction(INST_TYPE_COPY, size, mode)])

        # 12. - 17.
        for mode in range(6):
            for add_size in range(1, 5):
                for copy_size in range(4, 7):
                    code_table.append([Instruction(INST_TYPE_ADD, add_size, 0), Instruction(INST_TYPE_COPY, copy_size, mode)])

        # 18. - 20.
        for mode in range(6, 9):
            for add_size in range(1, 5):
                code_table.append([Instruction(INST_TYPE_ADD, add_size, 0), Instruction(INST_TYPE_COPY, 4, mode)])

        # 21.
        for mode in range(9):
            code_table.append([Instruction(INST_TYPE_COPY, 4, mode), Instruction(INST_TYPE_ADD, 1, 0)])

        assert len(code_table) == 256

        self = cls()
        self.s_near = DEFAULT_S_NEAR
        self.s_same = DEFAULT_S_SAME
        self.i_code = code_table
        return self


class VCDIFFCache:
    """Ported from example C code (Cache_t) from RFC 3284"""
    near: List[int]
    s_near: int
    next_slot: int
    same: List[int]
    s_same: int

    def __init__(self, s_near: int, s_same: int):
        self.s_near = s_near
        self.s_same = s_same

        self.near = [0] * self.s_near
        self.next_slot = 0
        self.same = [0] * (self.s_same * 256)

    def cache_update(self, addr: int) -> None:
        if self.s_near > 0:
            self.near[self.next_slot] = addr
            self.next_slot = (self.next_slot + 1) % self.s_near

        if self.s_same > 0:
            self.same[addr % (self.s_same * 256)] = addr


def apply_vcdiff_window(
        src: BinaryIO, diff: BinaryIO, out: BinaryIO,
        code_table: VCDIFFCodeTable, decompressors: XdeltaDecompressorTriple) -> None:
    """Apply a single VCDIFF window"""

    win_indicator = diff.read(1)[0]

    if win_indicator & VCD_TARGET:
        # not sure where to get example files to test win_indicator & VCD_TARGET...
        raise NotImplementedError('win_indicator & VCD_TARGET not yet supported')

    if win_indicator & (VCD_SOURCE | VCD_TARGET):
        src_seg_len = read_vcdiff_integer(diff)
        src_seg_pos = read_vcdiff_integer(diff)

    delta_encoding_len = read_vcdiff_integer(diff)
    target_window_len = read_vcdiff_integer(diff)
    delta_indicator = diff.read(1)[0]
    adds_runs_data_comp_len = read_vcdiff_integer(diff)
    instructions_data_comp_len = read_vcdiff_integer(diff)
    addresses_data_comp_len = read_vcdiff_integer(diff)

    if win_indicator & VCD_ADLER32:
        expected_adler = int.from_bytes(diff.read(4), 'big')

    adds_runs_data_comp = diff.read(adds_runs_data_comp_len)
    instructions_data_comp = diff.read(instructions_data_comp_len)
    addresses_data_comp = diff.read(addresses_data_comp_len)

    if delta_indicator & VCD_DATACOMP:
        adds_runs_data = decompressors.adds_runs.decompress_chunk(adds_runs_data_comp)
    else:
        adds_runs_data = adds_runs_data_comp

    if delta_indicator & VCD_INSTCOMP:
        instructions_data = decompressors.instructions.decompress_chunk(instructions_data_comp)
    else:
        instructions_data = instructions_data_comp

    if delta_indicator & VCD_ADDRCOMP:
        addresses_data = decompressors.addresses.decompress_chunk(addresses_data_comp)
    else:
        addresses_data = addresses_data_comp

    adds_runs_f = io.BytesIO(adds_runs_data)
    instructions_f = io.BytesIO(instructions_data)
    addresses_f = io.BytesIO(addresses_data)

    cache = VCDIFFCache(code_table.s_near, code_table.s_same)

    # Main loop
    out_buffer = _apply_vcdiff_window_inner_loop(
        src, src_seg_pos, src_seg_len,
        adds_runs_f, instructions_f, addresses_f, len(instructions_data),
        code_table, cache,
        target_window_len)

    if win_indicator & VCD_ADLER32:
        # Verify the Adler-32
        actual_adler = zlib.adler32(out_buffer)
        if expected_adler != actual_adler:
            print("WARNING: Adler-32 checksum didn't match!"
                f' (expected {expected_adler:08x}, got {actual_adler:08x}).'
                ' Output is probably wrong!')

    # Write output data
    out.write(out_buffer)


def _apply_vcdiff_window_inner_loop(
        src, src_seg_pos, src_seg_len,
        adds_runs_f, instructions_f, addresses_f, instructions_data_len,
        code_table, cache,
        target_window_len) -> bytearray:
    """Optimized namespace for the hot VCDIFF-instruction-processing loop"""

    # Assign this function to a local, so we can avoid global namespace lookups
    L_read_vcdiff_integer = read_vcdiff_integer

    # Avoid accidentally allocating 10 TB of memory or something.
    # 0x8000000 bytes = 128 MB -- arbitrary cutoff point I picked.
    # xdelta3 seems to use 8 MB as its max window size, so this is more
    # than enough.
    if target_window_len > 0x8000000:
        raise ValueError(f'Refusing to allocate memory for an enormous window size ({target_window_len})')

    # Create the output buffer
    out_buffer = bytearray(target_window_len)
    del target_window_len
    out_cursor = 0

    while instructions_f.tell() < instructions_data_len:

        inst_pair = code_table.i_code[instructions_f.read(1)[0]]

        for inst in inst_pair:

            if inst.size == 0:
                size = L_read_vcdiff_integer(instructions_f)
            else:
                size = inst.size

            if inst.type == 1:  # INST_TYPE_ADD
                out_buffer[out_cursor : out_cursor + size] = adds_runs_f.read(size)
                out_cursor += size

            elif inst.type == 2:  # INST_TYPE_RUN
                out_buffer[out_cursor : out_cursor + size] = adds_runs_f.read(1) * size
                out_cursor += size

            else:  # INST_TYPE_COPY -- note that there's no INST_TYPE_NOOP;
                   # we just omit nops from our inst pairs instead

                mode = inst.mode

                """Begin inlined addr_decode() from RFC 3284 section 5.4"""

                if mode == 0: # VCD_SELF
                    addr = L_read_vcdiff_integer(addresses_f)
                elif mode == 1: # VCD_HERE
                    addr = (src_seg_len + out_cursor) - L_read_vcdiff_integer(addresses_f)
                else:
                    m = mode - 2
                    if m >= 0 and m < cache.s_near:
                        addr = cache.near[m] + L_read_vcdiff_integer(addresses_f)
                    else:
                        addr = cache.same[(mode - (2 + cache.s_near)) * 256 + addresses_f.read(1)[0]]

                cache.cache_update(addr)

                """End inlined addr_decode()"""

                if addr < src_seg_len:
                    src.seek(src_seg_pos + addr)
                    out_buffer[out_cursor : out_cursor + size] = src.read(size)
                    out_cursor += size

                else:
                    addr -= src_seg_len

                    for _ in range(size):
                        out_buffer[out_cursor] = out_buffer[addr]
                        out_cursor += 1
                        addr += 1

    return out_buffer


def apply_vcdiff(src: BinaryIO, diff: BinaryIO, out: BinaryIO) -> Optional[bytes]:
    """
    Apply a VCDIFF (RFC 3284) patch to a file stream. Compatible with
    (most of) xdelta3's format extensions.

    src: the "source" file, which must be opened in binary-read mode.
    diff: the VCDIFF file, which must be opened in binary-read mode.
    out: the output file, which must be opened in binary-write mode.

    Returns the xdelta3 "appdata" (application-specific data -- a small
    bytestring from the file header), or None if there isn't any.
    """
    header_1234 = diff.read(4)

    if header_1234 != bytes.fromhex('D6 C3 C4 00'):
        raise ValueError(f'Wrong VCDIFF magic ({header_1234.hex()})')

    header_indicator = diff.read(1)[0]

    if header_indicator & VCD_DECOMPRESS:
        secondary_compression_type = diff.read(1)[0]
    else:
        secondary_compression_type = None
    decompressors = XdeltaDecompressorTriple.build_from_decompressor_value(secondary_compression_type)

    if header_indicator & VCD_CODETABLE:
        # Note: xdelta3 seems to not support this either
        raise NotImplementedError('Custom code tables not implemented')
    else:
        code_table = VCDIFFCodeTable.build_default()

    if header_indicator & VCD_APPHEADER:
        appdata = diff.read(read_vcdiff_integer(diff))
    else:
        appdata = None

    # After the header, a VCDIFF file is just a bunch of windows in a row.
    # So we apply them one by one until we reach the end of the file.
    diff_len = get_file_len(diff)
    while diff.tell() < diff_len:
        apply_vcdiff_window(src, diff, out, code_table, decompressors)

    return appdata


__all__ = ['apply_vcdiff']
