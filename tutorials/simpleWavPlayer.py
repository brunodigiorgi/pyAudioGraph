import pyAudioGraph as ag
import time

# 1. Create the units

world = ag.World(nchannels=2, buf_len=512)

wav_file = 'AudioFile.wav'  # only signed 16/32 bit supported
audioStream = ag.AudioStreamWaveFile(wav_file)
cmd_queue = ag.AsyncCmdQueue()

disk_in = ag.Nodes.DiskInNode(world, audioStream, cmd_queue=cmd_queue)
out_node = ag.Nodes.OutNode(world)

# 2. Connect the units

for i in range(disk_in.nchannels):
    disk_in.w_out[i].plug_into(out_node.w_in[i])

# 3. Append the output nodes
world.append(out_node)

# 4. Run 
world.start()
time.sleep(5)
world.stop()

cmd_queue.join()
