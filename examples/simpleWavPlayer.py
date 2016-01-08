import pyAudioGraph as ag

# 1. Create the units

world = ag.World(nchannels=2, buf_len=512)

wav_file = 'AudioFile.wav'  # only signed 16/32 bit supported
audioStream = ag.AudioStreamWaveFile(wav_file)
diskInUnit = ag.DiskInUnit(world, audioStream)

outUnit = ag.OutUnit(world)

# 2. Connect the units

for i in range(diskInUnit.nchannels):
    diskInUnit.w_out[i].plug_into(outUnit.w_in[i])

# 3. Create the sequence of unit calls

world.add_head(diskInUnit)
outUnit.add_after(diskInUnit)

# 4. Run 

import time
world.start()
time.sleep(5)
world.stop()