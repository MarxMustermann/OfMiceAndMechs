import tcod.sdl.audio
import soundfile as sf

sound_clip, samplerate = sf.read('sounds/electroRoom.ogg',dtype='float32')

device = tcod.sdl.audio.open()
device.queue_audio(sound_clip)  # Play audio synchronously.

mixer = tcod.sdl.audio.BasicMixer(device)
mixer.play(sound_clip)  # Play audio asynchronously.

import time
time.sleep(60)
