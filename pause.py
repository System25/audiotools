#!/usr/bin/python2

# Pauses detection software
#
# This script detects pauses in a speech and create different WAV files
# one each speech piece.

import wave
import sys
import struct

# Silent time in seconds
SILENT_TIME = 0.5


if len(sys.argv) < 3:
    print('Usage: {} infile.wav basename'.format(sys.argv[0]))
    sys.exit(1)

frame_size = 256
nfile = 0

infile = wave.open(sys.argv[1], 'rb')

if infile.getnchannels() > 1:
    print('Only support mono channel')
    sys.exit(2)

out = wave.open('{}_{:05d}.wav'.format(sys.argv[2], nfile), 'wb')
out.setnchannels(infile.getnchannels())
out.setsampwidth(infile.getsampwidth())
out.setframerate(infile.getframerate())

silent_frames = int(infile.getframerate()*SILENT_TIME)

print('infile - rate: {}, channels: {}, length: {}'.format(
        infile.getframerate(),
        infile.getnchannels(),
        infile.getnframes() / infile.getframerate()))

in_data_len = frame_size
in_data_bytes = frame_size * 2
out_data_len = frame_size
out_data_bytes = frame_size * 2


sf = 0
limit = 1000

in_data = infile.readframes(in_data_len)
while len(in_data) == in_data_bytes:
    out_data = ''

    # Compare current frame with the previous one looking for similitudes
    for index in range(0, in_data_len):
        pos = index*2
        sample = struct.unpack("<h", in_data[pos:pos+2])[0]

        if (sample >= -limit) and (sample <= limit):
            # Silent frame
            sf += 1
        else:
            # Frame with sound
            if sf >= silent_frames:
                # Close this file and open a new one
                out.close()
                nfile += 1
                out = wave.open('{}_{:05d}.wav'.format(sys.argv[2], nfile), 'wb')
                out.setnchannels(infile.getnchannels())
                out.setsampwidth(infile.getsampwidth())
                out.setframerate(infile.getframerate())
                
            sf = 0
            
        out_data += in_data[pos]
        out_data += in_data[pos+1]



    out.writeframes(out_data)

    in_data = infile.readframes(in_data_len)

infile.close()
out.close()
