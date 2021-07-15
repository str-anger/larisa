import configparser
import logging
import sound.rec as r
import logic.processor as prc

def start_text_interface(cfg):
    logging.info("Starting text interface. Type `exit` to finish")
    command = None
    while command != "exit":
        print("ask> ", end="")
        command = input()
        prc.process(command, cfg, logging)

def start_web_interface(cfg):
    pass


def start_voice_interface(cfg):
    # r.record(5)
    # print(len(r))
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