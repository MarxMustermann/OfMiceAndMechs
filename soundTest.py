import tcod.sdl.audio
import soundfile as sf

sound_clip, samplerate = sf.read('sounds/electroRoom.ogg',dtype='float32')

device = tcod.sdl.audio.open()
#device.queue_audio(sound_clip)  # Play audio synchronously.

mixer = tcod.sdl.audio.BasicMixer(device)
mixer.start()
channel = mixer.get_channel("test")
channel.play(sound_clip)

import time
time.sleep(60)
