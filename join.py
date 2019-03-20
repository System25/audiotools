#!/usr/bin/python2

# Join pieces of speech.
#
# This script joins pieces of speech in different two files (good and bad) by calculating the pitch.

import wave
import sys
import struct
import os
from aubio import source, pitch



if len(sys.argv) < 3:
    print('Usage: {} basename_in basename_out'.format(sys.argv[0]))
    sys.exit(1)

npiece = 0
nfiles = 2
names = []
names.append('bad')
names.append('good')


filename = '{}_{:05d}.wav'.format(sys.argv[1], npiece)
if not os.path.isfile(filename):
    print "File %s does not exist!"
    sys.exit(1)

infile = wave.open(filename, 'rb')
nchannels = infile.getnchannels()
sampwidth = infile.getsampwidth()
framerate = infile.getframerate()
infile.close()
    
out = [None] * nfiles

# Create output files
for i in range(0, nfiles):
    out[i] = wave.open('{}_{}.wav'.format(sys.argv[2], names[i]), 'wb')
    out[i].setnchannels(nchannels)
    out[i].setsampwidth(sampwidth)
    out[i].setframerate(framerate)

# Read each piece
filename = '{}_{:05d}.wav'.format(sys.argv[1], npiece)
while os.path.isfile(filename):
    nf = 0 # Default output
    
    # Use aubio to calculate the pitch
    win_s = 4096 # fft size
    hop_s = 512  # hop size
    s = source(filename, framerate, hop_s)
    framerate = s.samplerate

    tolerance = 0.8

    pitch_o = pitch("yin", win_s, hop_s, framerate)
    pitch_o.set_unit("midi")
    pitch_o.set_tolerance(tolerance)
    
    ac_pitch = 0
    confidences = []
    pitches = []

    # total number of frames read
    total_frames = 0
    total_pitches = 0
    max_pitch = 0
    min_pitch = 100.0
    while True:
        samples, read = s()
        pitchv = pitch_o(samples)[0]
        confidence = pitch_o.get_confidence()
        if confidence < 0.8:
            pitchv = 0
        elif pitchv > 0:
            total_pitches += 1
            if pitchv > max_pitch:
                max_pitch = pitchv
                
            if pitchv < min_pitch:
                min_pitch = pitchv
            
            pitches.append(pitchv)
            

        ac_pitch += pitchv
        total_frames += read
        
        if read < hop_s: break

    median_pitch = 0
    if total_pitches > 0:
        medium_pitch = ac_pitch / total_pitches
        median_pitch = pitches[int(total_pitches / 2)]
    else:
        medium_pitch = 0;
    
    delta = (max_pitch - min_pitch)
    print "============================================="
    print "(%d) Medium pitch: %f"%(npiece, medium_pitch)
    print "(%d) Median pitch: %f"%(npiece, median_pitch)
    print "(%d) Maximum pitch: %f"%(npiece, max_pitch)
    print "(%d) Minimum pitch: %f"%(npiece, min_pitch)
    print "(%d) Max-Min diffe: %f"%(npiece, (max_pitch - min_pitch))
    print "(%d) Max-Min mediu: %f"%(npiece, (max_pitch + min_pitch)/2)
    
    # Custom rules
    if (medium_pitch > 10.0) and (median_pitch <= 85) and (delta > 10):
        # Good sound?
        nf = 1

    
    print "%s?"%(names[nf])
    
    infile = wave.open(filename, 'rb')
    nframes = infile.getnframes() 
    in_data = infile.readframes(nframes)
    infile.close()
    
    emptydata = ''
    for i in range(0, nframes*2):
        emptydata += '\0'
    
    for i in range(0, nfiles):
        if i == nf:
            out[i].writeframes(in_data)
        else:
            out[i].writeframes(emptydata)
    
    npiece += 1
    filename = '{}_{:05d}.wav'.format(sys.argv[1], npiece)

    
# Close output files
for i in range(0, nfiles):
    out[i].close()
    
