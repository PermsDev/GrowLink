
from . import setup_intro
from . import setup_promote
from . import ping


COMMAND_HELP = {
    setup_intro.NAME: setup_intro,
    setup_promote.NAME: setup_promote,
    ping.NAME: ping,
}
