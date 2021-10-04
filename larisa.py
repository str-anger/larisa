import configparser
import logging
import logic.processor as prc
import speech_recognition as sr
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator as IAMA
import sounddevice
import requests
from geopy import Nominatim


def temperature_conversion(temp):
    '''
    #Author: Nils Becker
    Converts a given temperature in °K into a °C String representation
    :param temp: Float Value of temperature in °K
    :returns: The temperature converted to °C as a String
    '''
    return f"{int(temp)-273}°C"

def weather_forecast(cfg, city):
    '''
    #Author: Nils Becker
    Gives a weather forecast for a specified city
    :param cfg: Currently used configuration
    :param city: String representation of city
    :returns: weather forecast for now/ next 12h/ next 7 days in a List
    '''
    locator = Nominatim(user_agent="Larissa")
    location = locator.geocode(city)
    #get free key from https://openweathermap.org/
    api_key = cfg['weather']['apikey']
    try:
    #create API request for given city
        url = 'https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&exclude={}&appid={}'.format(location.latitude, location.longitude, "minutely,alerts", api_key)
        response = requests.get(url).json()
    except AttributeError:
        logging.error(f"City {city} not found!")
        return None
    result = []
    try:
    #get data
        current = response['current']
        currentList = []
        temperature = temperature_conversion(current['temp'])
        weather = current['weather']
        description = weather[0]['description']
        clouds = str(current['clouds']) + "%"+" clouds"
        currentList.append(temperature)
        currentList.append(description)
        currentList.append(clouds)
        result.append([currentList])
        for option in ["hourly", "daily"]:
            #get hourly, then daily data

            currentList=[]
            current = response[option]
            #if option == hourly, the next 12 hours are relevant -> length = 13
            #if option == daily, the next 7 days are relevant -> length 8
            length = 13 if option == "hourly" else 8 
            for i in range (1, length):
                #loop through the next 12 hours or next 7 days

                temporary = current[i]
                loopList=[i]
                if option == "daily":
                    temp = temporary['temp']
                    average = temperature_conversion(temp['day'])
                    min = temperature_conversion(temp['min'])
                    max = temperature_conversion(temp['min'])
                    loopList.append(average)
                    loopList.append(min)
                    loopList.append(max)
                else:
                    temperature = temperature_conversion(temporary['temp'])
                    loopList.append(temperature)
                weather = temporary['weather']
                description = weather[0]['description']
                clouds = f"{temporary['clouds']}% clouds"
                pop = f"{temporary['pop']*100}% chance of precipation"
                loopList.append(description)
                loopList.append(clouds)
                loopList.append(pop)
                currentList.append(loopList)
            result.append(currentList)
    except TypeError:
        logging.error("Weather API Error")
        return None    
    return result
    
def start_text_interface(cfg):
    logging.info("Starting text interface. Type `stop` to finish")
    command = None
    while command != "stop":
        print("ask> ", end="")
        command = input()
        result = prc.process(command, cfg, logging)
        print(result)

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

    keywords = cfg['audio']['keywords'].split()
    stopword = cfg['audio']['stopword']
    recognizer_type = cfg['audio']['recognizer']
    logging.info(f"Keyword = {keywords}, stopword = {stopword}, Recognizer = {recognizer_type}")
    command = None
    ibm_auth, ibm_recognizer = None, None
    # use this code: https://stackoverflow.com/questions/48777294/python-app-listening-for-a-keyword-like-cortana
    # get audio from the microphone
    r = sr.Recognizer()
    # r.dynamic_energy_threshold = False

    while command != stopword:
        # wait for a trigger word
        
        with sr.Microphone() as source:
           print("Waiting for a word ...")
           r.adjust_for_ambient_noise(source)
           audio = r.listen(source)
            #test the data comes
           logging.info(f"Len: {len(audio.frame_data)}, Data: {audio.frame_data[:16]}")

        # simple way to replace if you don't have a micro
        # with sr.AudioFile("/mnt/c/dev/voice.wav") as af:
        #     audio = r.record(af)

        try:
            # recognize a word
            if 'sphinx' == recognizer_type:
                logging.info("Using sphinx")
                recognized = r.recognize_sphinx(audio, keyword_entries=[(kw, 1.0) for kw in keywords]).strip()
            elif 'wit' == recognizer_type:
                logging.info("using wit")
                recognized = r.recognize_wit(audio, key=cfg['service']['wit']['access_token']).strip()
            elif 'ibm' == recognizer_type:
                logging.info("using IBM")
                if ibm_auth is None:
                    logging.info('Instantiating IBM recognizer')
                    ibm_auth = IAMA(apikey=cfg['ibm']['apikey'])
                    ibm_recognizer = SpeechToTextV1(authenticator=ibm_auth)
                    ibm_recognizer.set_service_url(cfg['ibm']['url'])
                logging.info('Recognizing IBM')
                recognized = ibm_recognizer.recognize(audio=audio.get_wav_data(), content_type='audio/wav').get_result()
                logging.info(recognized)
                recognized = recognized['results'][0]['alternatives'][0]['transcript'].strip() if recognized['results'] else ''

            logging.info(f"word `{recognized}` captured")
            # if this was a keyword - process a command
            if recognized.strip().lower() in keywords:
                print('Waiting for a command...')
                with sr.Microphone() as source:
                    r.adjust_for_ambient_noise(source)
                    command_audio = r.listen(source)
                if 'sphinx' == recognizer_type:
                    command = r.recognize_sphinx(command_audio)
                elif 'wit' == recognizer_type:
                    command = r.recognize_wit(command_audio, key=cfg['service']['wit']['access_token'])
                elif 'ibm' == recognizer_type:
                    command = ibm_recognizer.recognize(audio=command_audio.get_wav_data(), content_type='audio/wav').get_result()
                    logging.info(command)
                    command = command['results'][0]['alternatives'][0]['transcript'].strip() if command['results'] else ''
                # exit on stop word
                if command == stopword:
                    logging.info('Exit on stopword')
                    break
                result = prc.process(command, cfg, logging)
                # TODO: SPEAK THE RESULT
                print(result)
        except sr.UnknownValueError:
            logging.error("Could not understand audio")
        except sr.RequestError as e:
            logging.error(f"Could not request results: {e}")
        pass


if __name__ == "__main__":
    sounddevice.query_devices()
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
