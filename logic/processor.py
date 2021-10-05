import requests
from geopy import Nominatim

class Response:
    def __init__(self, text=None, payload=None, status='ok'):
        self.text = text
        self.payload = payload
        self.status = status

    def __repr__(self):
        return f"[{self.status}] {self.text}"

    def __str__(self):
        return self.__repr__()


def _get_intent(text):
    """
    This function should compute the intent of the request, and then in will be passed to the corresponding service
    """
    if 'coffee' in text:
        return 'coffee'
    if 'translate' in text:
        return 'translate'
    if 'weather' in text:
        return 'weather'

    #TODO: implement

    return None



def _coffee(text):
    return Response(text=f"Cannot perform `{text}` - I'm a teapot")


def _translate(text):
    return Response(text="")

    
def temperature_conversion(temp,logging):
    '''
    #Author: Nils Becker
    Converts a given temperature in °K into a °C String representation
    :param temp: Float or int Value of temperature in °K
    :returns: The temperature converted to °C as a String
    '''
    try:
        return f"{int(temp)-273}°C"
    except ValueError:
        logging.error(f"{temp} must be an int or float")
        pass

def _weather(cfg, city, logging):
    '''
    #Author: Nils Becker
    Gives a weather forecast for a specified city
    :param cfg: Currently used configuration
    :param city: String representation of city
    :returns: weather forecast for now/ next 12h/ next 7 days in a List
    '''
    locator = Nominatim(user_agent="Larissa")
    location = locator.geocode(city)
    #get key from https://openweathermap.org/
    api_key = cfg['weather']['apikey']
    try:
        #create API request for given city
        url = 'https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&exclude={}&appid={}'.format(location.latitude, location.longitude, "minutely,alerts", api_key)
        response = requests.get(url).json()
    except AttributeError:
        logging.error(f"City {city} not found!")
        return []
    result = []
    try:
        #get data
        current = response['current']
        currentList = []
        temperature = temperature_conversion(current['temp'], logging)
        weather = current['weather']
        description = weather[0]['description']
        clouds = f"{current['clouds']}% clouds"
        currentList.append(temperature)
        currentList.append(description)
        currentList.append(clouds)
        result.append([currentList])
        for option in ["hourly", "daily"]:
            #get hourly, then daily data

            currentList = []
            current = response[option]
            #if option == hourly, the next 12 hours are relevant -> length = 13
            #if option == daily, the next 7 days are relevant -> length 8
            length = 13 if option == "hourly" else 8 
            for i in range (1, length):
                #loop through the next 12 hours or next 7 days

                temporary = current[i]
                loopList = [i]
                if option == "daily":
                    temp = temporary['temp']
                    average = temperature_conversion(temp['day'], logging)
                    min = temperature_conversion(temp['min'], logging)
                    max = temperature_conversion(temp['min'], logging)
                    loopList.append(average)
                    loopList.append(min)
                    loopList.append(max)
                else:
                    temperature = temperature_conversion(temporary['temp'], logging)
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
    except KeyError as e:
        logging.error(f"{e} Weather API Error: Field {e} not available")
        return [] 
    except TypeError as e:
        logging.error("Weather API Error: Field {e} returned None")
        return []    
    return Response(text = result)



def process(command, cfg, logging):
    logging.info(f"Processing command `{command}`")
    intent = _get_intent(command)
    if 'coffee' == intent:
        return _coffee(command)
    elif 'translate' == intent:
        return _translate(text)
    elif 'weather' == intent:
        return _weather(cfg, "Innopolis", logging)

    return None
