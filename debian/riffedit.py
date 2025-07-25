#!/usr/bin/python3
# coding: UTF-8
#-
# Copyright © 2018, 2020 Thorsten Glaser <tg@mirbsd.de>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#-
# python3 riffedit.py -d src.sf2  # dump info only
# python3 riffedit.py -i src.sf2  # identify metadata (see below)
# python3 riffedit.py src.sf2 dst.sf2 { [-az] 'chnk' 'content' } ...
#  where -a means to align with NULs and -z to NUL-terminate
#  chnk means the RIFF chunk, LIST<chnk>/chnk is also supported
# Chunks currently need to exist in the input, insertion and deletion
# is missing for some later version to add.
# The comment field is limited to 65535 ASCII bytes, the others to 255.
#
# Metadata from a soundfont only includes chunks useful in copyright
# tracking. It outputs the INFO chunks, using input ordering, in the
# format “chunk_name \xFE chunk_body \xFF”, where both name and body
# (properly UTF-8 encoded) have all characters not valid for XML re‐
# moved or replaced with the OPTU-16 value or U+FFFD.
#
# You may also use this under the terms of The MirOS Licence instead.

from io import SEEK_SET, SEEK_CUR
import os
import struct
import sys

assert(sys.version_info[0] >= 3)

class RIFFChunk(object):
    def __init__(self, parent):
        self.parent = parent
        self.file = parent
        while isinstance(self.file, RIFFChunk):
            self.file = self.file.parent

        cn = self.file.read(4)
        cs = self.file.read(4)
        ct = None
        cf = cn
        if (len(cn) != 4) or (len(cs) != 4):
            raise EOFError
        co = self.file.tell()
        try:
            cs = struct.unpack_from('<L', cs)[0]
        except struct.error:
            raise EOFError
        if cn in (b'RIFF', b'LIST'):
            ct = self.file.read(4)
            if len(ct) != 4:
                raise EOFError
            cf = cn + b'<' + ct + b'>'

        self.chunkname = cn
        self.chunksize = cs
        self.chunk_pad = cs & 1
        self.container = ct
        self.children = []
        self.chunkfmt = cf
        self.data_ofs = co
        self.data_mem = None
        self.justpast = self.data_ofs + self.chunksize + self.chunk_pad

        if isinstance(self.parent, RIFFChunk) and \
          self.justpast > self.parent.justpast:
            raise IndexError('End of this %s chunk %d > end of parent %s chunk %d' % \
              (self.chunkfmt, self.justpast, self.parent.chunkfmt, self.parent.justpast))

        if self.container is not None:
            while True:
                try:
                    child = RIFFChunk(self)
                except EOFError:
                    break
                self.children.append(child)
                if child.skip_past():
                    break

    def __str__(self):
        s = '<RIFFChunk(%s)' % self.chunkfmt
        if self.container is not None:
            q = '['
            for child in self.children:
                s += q + str(child)
                q = ', '
            s += ']'
        return s + '>'

    def skip_past(self):
        self.file.seek(self.justpast, SEEK_SET)
        return isinstance(self.parent, RIFFChunk) and \
          self.justpast == self.parent.justpast

    def __getitem__(self, key):
        if self.container is None:
            raise IndexError('Chunk %s is not of a container type' % self.chunkname)
        for child in self.children:
            if child.chunkfmt == key:
                return child
        raise IndexError('Chunk %s does not have a child %s' % (self.chunkname, key))

    def print(self):
        if self.container is not None:
            raise IndexError('Chunk %s is of a container type' % self.chunkname)
        if self.data_mem is not None:
            return self.data_mem
        self.file.seek(self.data_ofs, SEEK_SET)
        s = self.file.read(self.chunksize)
        if len(s) != self.chunksize:
            raise IOError('Could not read %d data bytes (got %d)' % (self.chunksize, len(s)))
        return s

    def write(self, file):
        if not isinstance(self.chunkname, bytes):
            raise ValueError('Chunk name %s is not of type bytes' % self.chunkname)
        if len(self.chunkname) != 4:
            raise ValueError('Chunk name %s is not of length 4')
        if file.write(self.chunkname + struct.pack('<L', self.chunksize)) != 8:
            raise IOError('Could not write header bytes to destination file at chunk %s' % \
              self.chunkfmt)
        if self.container is not None:
            cld = file.tell()
            if not isinstance(self.container, bytes):
                raise ValueError('Container type %s is not of type bytes' % self.container)
            if len(self.container) != 4:
                raise ValueError('Container type %s is not of length 4')
            if file.write(self.container) != 4:
                raise IOError('Could not write container bytes to destination file at chunk %s' % \
                  self.chunkfmt)
            for child in self.children:
                child.write(file)
            cld = file.tell() - cld
            if cld != self.chunksize:
                raise ValueError('Children wrote %d bytes (expected %d) file at chunk %s' % \
                  (cld, self.chunksize, self.chunkfmt))
        else:
            if self.data_mem is not None:
                if file.write(self.data_mem) != self.chunksize:
                    raise IOError('Could not write %d data bytes to destination file at chunk %s' % \
                      (self.chunksize, self.chunkfmt))
            else:
                self.file.seek(self.data_ofs, SEEK_SET)
                total = self.chunksize
                while total > 0:
                    n = 65536
                    if n > total:
                        n = total
                    buf = self.file.read(n)
                    n = len(buf)
                    total -= n
                    if file.write(buf) != n:
                        raise IOError('Could not write %d data bytes to destination file at chunk %s' % \
                          (n, self.chunkfmt))
        if self.chunk_pad > 0:
            file.write(b'\0')
        if file.tell() & 1:
            raise ValueError('Misaligned file after chunk %s' % self.chunkfmt)

    def set_length(self, newlen):
        old = self.chunksize + self.chunk_pad
        self.chunksize = newlen
        self.chunk_pad = self.chunksize & 1
        new = self.chunksize + self.chunk_pad
        if isinstance(self.parent, RIFFChunk):
            self.parent.adjust_length(new - old)

    def set_content(self, content, nul_pad=False):
        if self.container is not None:
            raise ValueError('Cannot set content of container type %s' % self.chunkfmt)
        if isinstance(content, str):
            content = content.encode('UTF-8')
        if not isinstance(content, bytes):
            raise ValueError('New content is not of type bytes')
        if nul_pad and (len(content) & 1):
            content += b'\0'
        self.data_mem = content
        self.set_length(len(content))

    def adjust_length(self, delta):
        self.set_length(self.chunksize + delta)

class RIFFFile(RIFFChunk):
    def __init__(self, file):
        self.file = file
        self.container = True
        self.children = []

        child = None
        while True:
            try:
                child = RIFFChunk(f)
            except EOFError:
                break
            self.children.append(child)

        if child is None:
            raise IndexError('No RIFF chunks found')

        self.justpast = child.justpast

    def __str__(self):
        s = '<RIFFFile'
        q = '['
        for child in self.children:
            s += q + str(child)
            q = ', '
        return s + ']>'

    def __getitem__(self, key):
        return self.children[key]

    def write(self, file):
        for child in self.children:
            child.write(file)

def dumpriff(container, level=0, isinfo=False):
    indent = ('%s%ds' % ('%', 2*level)) % ''
    print(indent + 'BEGIN level=%d' % level)
    for chunk in container.children:
        #print(indent + ' CHUNK %s of size %d, data at %d, next at %d' % (chunk.chunkfmt, chunk.chunksize, chunk.data_ofs, chunk.justpast))
        if isinfo:
            print(indent + ' CHUNK %s(%d): %s' % (chunk.chunkfmt, chunk.chunksize, chunk.print()))
        else:
            print(indent + ' CHUNK %s of size %d' % (chunk.chunkfmt, chunk.chunksize))
        if chunk.container is not None:
            dumpriff(chunk, level+1, chunk.chunkfmt == b'LIST<INFO>')
    print(indent + 'END level=%d' % level)

if sys.argv[1] == '-i':
    encode_table = {}
    # bad characters in XML
    for i in range(0, 32):
        if i not in (0x09, 0x0A, 0x0D):
            encode_table[i] = None
    encode_table[0x7F] = 0xFFFD
    for i in range(0x80, 0xA0):
        encode_table[i] = 0xEF00 + i
    for i in range(0xD800, 0xE000):
        encode_table[i] = 0xFFFD
    for i in range(0, 0x110000, 0x10000):
        encode_table[i + 0xFFFE] = 0xFFFD
        encode_table[i + 0xFFFF] = 0xFFFD
    for i in range(0xFDD0, 0xFDF0):
        encode_table[i] = 0xFFFD
    # surrogateescape to OPTU-16
    for i in range(128, 256):
        encode_table[0xDC00 + i] = 0xEF00 + i
    ident_encode_table = str.maketrans(encode_table)
    del encode_table

    def ident_encode(s):
        return s.rstrip(b'\x00').\
          decode(encoding='utf-8', errors='surrogateescape').\
          translate(ident_encode_table).\
          encode(encoding='utf-8', errors='replace')

    if sys.argv[2] == '-':
        f = sys.stdin.buffer
    else:
        f = open(sys.argv[2], 'rb')
    riff = RIFFFile(f)
    for chunk in riff[0][b'LIST<INFO>'].children:
        if chunk.chunkname not in (b'ifil', b'isng', b'IPRD', b'ISFT'):
            for x in (ident_encode(chunk.chunkname), b'\xFE',
              ident_encode(chunk.print()), b'\xFF'):
                sys.stdout.buffer.write(x)
    sys.exit(0)

print('START')
if sys.argv[1] == '-d':
    with open(sys.argv[2], 'rb') as f:
        riff = RIFFFile(f)
        dumpriff(riff)
else:
    with open(sys.argv[1], 'rb') as f, open(sys.argv[2], 'wb', buffering=65536) as dst:
        riff = RIFFFile(f)
        dumpriff(riff)
        i = 3
        _flags = { '-a': 1, '-z': 2, '-az': 3 }
        while i < len(sys.argv):
            flags = 0
            if sys.argv[i] in _flags:
                flags = _flags[sys.argv[i]]
                i += 1
                if i >= len(sys.argv):
                    break
            chunks = sys.argv[i].split('/')
            if chunks[0].isnumeric():
                chnk = riff
            else:
                chnk = riff[0]
            for cur in chunks:
                chnk = chnk[os.fsencode(cur)]
            val = os.fsencode(sys.argv[i + 1])
            if flags & 2:
                val += b'\0'
            chnk.set_content(val, bool(flags & 1))
            i += 2
        print("=> after processing:")
        dumpriff(riff)
        riff.write(dst)
print('OUT')
