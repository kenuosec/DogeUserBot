from . import fonts
from . import memeshelper as dogememes
from .aiohttp_helper import AioHttp
from .utils import *

flag = True
check = 0
while flag:
    try:
        from . import nsfw as hub
        from .functions import *
        from .progress import *
        from .qhelper import process
        from .tools import *
        from .utils import _dogetools, _dogeutils, _format

        # from .chatbot import *
        # from .torrentutils import *
        break
    except ModuleNotFoundError as e:
        install_pip(e.name)
        check += 1
        if check > 5:
            break
