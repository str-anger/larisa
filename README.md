# Larisa
Voice assistant - education project for 
[applied AI](https://github.com/hsu-ai-course/hsu.ai/) course.


Initially designed for Raspberry Pi model B (the old one) this project contains some derived limitations and hacks:
- run `install_pyaudio_with_patch.sh` with `su` rights to make pyaudio work in raspbian (according to [this](https://stackoverflow.com/questions/59006083/how-to-install-portaudio-on-pi-properly))
- download the models with `download_models.sh` script
- not sure you can make it run in Windows...

## Install guide
1. Tune `config.ini`. What is important? If you use voice, choose correct playback and recording devices. Call `sounddevice.query_devices()` in python to learn their ids.
2. Specify host IP and port if you use web.
3. run `install_pyaudio_with_patch.sh` with superuser.
4. Install `pip install -r requirements.txt`.

