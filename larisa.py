import configparser
import logging
# import sound.rec as r
import logic.processor as prc
import speech_recognition as sr


def start_text_interface(cfg):
    logging.info("Starting text interface. Type `stop` to finish")
    command = None
    while command != "stop":
        print("ask> ", end="")
        command = input()
        prc.process(command, cfg, logging)


def start_web_interface(cfg):
    """
    Starts the server processing requests via web interface
    :param cfg: config dictionary used to get server parameters
    :return: this launches an event loop. Returns when finished
    """
    logging.warning("Not implemented yet")
    pass


def start_voice_interface(cfg):
    """
    Starts the voice loop
    :param cfg:
    :return:
    """
    # https://github.com/MycroftAI/mimic1
    # https://pypi.org/project/SpeechRecognition/

    keyword = cfg['audio']['keyword']
    stopword = cfg['audio']['stopword']
    command = None
    # use this code: https://stackoverflow.com/questions/48777294/python-app-listening-for-a-keyword-like-cortana
    # get audio from the microphone
    r = sr.Recognizer()
    while command != stopword:
        # wait for a trigger word
        with sr.Microphone() as source:
            print("Waiting for a word ...")
            audio = r.listen(source)

        # simple way to replace if you don't have a micro
        # with sr.AudioFile("/mnt/c/dev/voice.wav") as af:
        #     audio = r.record(af)

        try:
            # recognize a word
            recognised = r.recognize_wit(audio, key=cfg['service']['wit_access_token'])
            logging.info(f"word `{recognised}` captured")
            # if this was a keyword - process a command
            if recognised == keyword:
                command_audio = r.listen(source)
                command = r.recognize_wit(command_audio, key=cfg['service']['wit_access_token'])
                # exit on stop word
                if command == stopword:
                    break
                result = prc.process(command, cfg, logging)
                # TODO: SPEAK THE RESULT OUT LOUD
        except sr.UnknownValueError:
            print("Could not understand audio")
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))
        pass


if __name__ == "__main__":
    logging.basicConfig(format='[%(asctime)s][%(levelname)s] %(message)s', level=logging.INFO)
    logging.info("Larisa is starting")
    config = configparser.ConfigParser()
    config.read('config.ini')
    if 'ui' not in config:
        logging.error("Config section [ui] is missing")
        exit(1)
    mode = config['ui']['mode']
    if 'text' == mode:
        start_text_interface(config)
    elif 'web' == mode:
        start_web_interface(config)
    elif 'voice' == mode:
        start_voice_interface(config)
    else:
        logging.error("unknown ui mode")
        exit(2)
    
    logging.info("Smoothly finishing")
