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

    #TODO: implement

    return None



def _coffee(text):
    return Response(text=f"Cannot perform `{text}` - I'm a teapot")


def _translate(text):
    return Response(text="")


def process(command, cfg, logging):
    logging.info(f"Processing command `{command}`")
    intent = _get_intent(command)
    if 'coffee' == intent:
        return _coffee(command)
    elif 'translate' == intent:
        return _translate(text)

    return None
