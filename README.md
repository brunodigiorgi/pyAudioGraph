[![Docs](https://readthedocs.org/projects/pyaudiograph/badge/?version=latest)](https://pyaudiograph.readthedocs.io/en/latest/?badge=latest)
[![Build](https://travis-ci.org/brunodigiorgi/pyAudioGraph.svg)](https://travis-ci.org/brunodigiorgi/pyAudioGraph)
[![License](https://img.shields.io/badge/license-GPLv2-blue.svg)](https://raw.githubusercontent.com/brunodigiorgi/pyAudioGraph/master/LICENSE)

Requirements
------------

* [pyAudio](http://people.csail.mit.edu/hubert/pyaudio/)
* numpy

Installation
------------

Install portaudio on mac (tested on osx 10.11):
	
	mkdir portaudio_trunk
	svn co https://subversion.assembla.com/svn/portaudio/portaudio/trunk/ portaudio_trunk --non-interactive --trust-server-cert
	cd portaudio_trunk
	
	./configure
	make 
	make install

Install portaudio on windows 7 (mingw):
	
	./configure
	make 
	make install

Install portaudio on windows 7 (msvc with visual-cpp-build-tools http://landinghub.visualstudio.com/visual-cpp-build-tools):

	cd build/msvc/
	path/to/vcvarsall.bat x64
	cmake -G "Visual Studio 14 2015 Win64" ../../
	MSBuild portaudio.sln

Install pyAudio

	pip3 install pyAudio

Depending on where you installed portaudio you may need to add its path:

	pip3 install --global-option=build_ext --global-option="-I/usr/local/include" pyAudio

Install pyAudioGraph

	python3 setup.py install

Usage
-----
	
see Tutorials/

Conventions
-----------

* Sound buffers are numpy.ndarray with shape (channels, samples)
* Units are connected using wires (audio-rate and control-rate)
* Connections are estabilished between an output Wire and an input Wire with the method Wire.plug_into(Wire)
* Wires are prefixed with w_ for easy usage with code completion
* Sometimes input control-rate wires change parameters of the units (for example: SinOsc.w_freq). The method set_value is threadsafe, so that you can for example change the frequency of the oscillator from the main/gui thread by calling SinOsc.w_freq.set_value()

General Usage
-------------

	import pyAudioGraph as ag

Create and connect the units.
Then add all the output units and compile the graph

	world.append(output_units)
	world.sort()

Run the audio graph

	import time
	world.start()
	time.sleep(20)
	world.stop()

Other Units
-----------

Sampler

	samplerUnit = ag.SamplerUnit(world, 1)
	sineBuffer = 0.2 * np.sin(np.arange(44100) * 400 / 44100 * 2 * np.pi).reshape(1,-1)
	samplerUnit.add_buffer(sineBuffer)

Mixer

	M = np.array([[1,0,1,0,1],
				  [0,1,0,1,1]]) 
	mixer = ag.MixerUnit(world, M)

	diskInUnit1.w_out[0].plug_into(mixer.w_in[0])
	diskInUnit1.w_out[1].plug_into(mixer.w_in[1])
	diskInUnit2.w_out[0].plug_into(mixer.w_in[2])
	diskInUnit2.w_out[1].plug_into(mixer.w_in[3])
	samplerUnit.w_out[0].plug_into(mixer.w_in[4])

Oscillator
	
	sinOsc = ag.SinOsc(world)
	sinOsc.w_freq.set_value(400)

InUnit (mic)

	inUnit = ag.InUnit(world)

Recorder

	rec_cr = ag.ControlRateRecorder(world, 1)
	rec_ar = ag.AudioRateRecorder(world, 1)
	inUnit.w_out[0].plug_into(rec_ar.w_in[0])


