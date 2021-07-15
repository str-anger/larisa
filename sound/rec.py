import sounddevice as sd

SAMPLE_RATE = 22050
CHANNELS = 2

# sd.default.samplerate = SAMPLE_RATE
sd.default.channels = 0 # CHANNELS
sd.default.device = 1

def record(duration_sec=10):
    print(sd.query_devices())
    return sd.rec(int(duration_sec * SAMPLE_RATE))
