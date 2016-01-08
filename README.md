[![License](https://travis-ci.org/brunodigiorgi/pyAudioGraph.svg)](https://travis-ci.org/brunodigiorgi/pyAudioGraph)
[![License](https://img.shields.io/badge/license-GPLv2-blue.svg)](https://raw.githubusercontent.com/brunodigiorgi/pyAudioGraph/master/LICENSE)

Requirements
------------

* [pyAudio](http://people.csail.mit.edu/hubert/pyaudio/)
* numpy

Installation
------------

	python3 setup.py install

Usage
-----
	
	import pyAudioGraph as ag

	# 1. Create the units

	world = ag.World(nchannels=2, buf_len=512)

	wav_file = 'outputFile.wav'  # only signed 16/32 bit supported
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

Conventions
-----------

* Sound buffers are numpy.ndarray with shape (nChannels, nSamples)
* Units are connected using wires (audio-rate and control-rate)
* Connections are estabilished between an output Wire and an input Wire with the method Wire.plugInto(Wire)
* Wires are prefixed with w_ for easy usage with code completion
* Sometimes input control-rate wires change parameters of the units (for example: SinOsc.w_freq). The method setValue is threadsafe, so that you can for example change the frequency of the oscillator from the main/gui thread by calling SinOsc.w_freq.setValue()

Other Units
-----------

#### Sampler

	samplerUnit = ag.SamplerUnit(world, 1)
	sineBuffer = 0.2 * np.sin(np.arange(44100) * 400 / 44100 * 2 * np.pi).reshape(1,-1)
	samplerUnit.addBuffer(sineBuffer)

#### Mixer

	M = np.array([[1,0,1,0,1],
				  [0,1,0,1,1]]) 
	mixer = ag.MixerUnit(world, M)

	diskInUnit1.w_out[0].plugInto(mixer.w_in[0])
	diskInUnit1.w_out[1].plugInto(mixer.w_in[1])
	diskInUnit2.w_out[0].plugInto(mixer.w_in[2])
	diskInUnit2.w_out[1].plugInto(mixer.w_in[3])
	samplerUnit.w_out[0].plugInto(mixer.w_in[4])

#### Oscillator
	
	sinOsc = ag.SinOsc(world)
	sinOsc.w_freq.setValue(400)

#### InUnit (mic)

	inUnit = ag.InUnit(world)

#### Recorder

	rec_cr = ag.ControlRateRecorder(world, 1)
	rec_ar = ag.AudioRateRecorder(world, 1)
	inUnit.w_out[0].plugInto(rec_ar.w_in[0])


