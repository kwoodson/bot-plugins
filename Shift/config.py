

import supybot.conf as conf
import supybot.utils as utils
import supybot.registry as registry

def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('Shift', True)
    if yn(""" This allows the ability to get all: in a channel and 
                translate it to names""", default=True):
        conf.supybot.plugins.Shift.shiftSnarfer.setValue(True)

Shift = conf.registerPlugin('Shift')
#conf.registerChannelValue(Shift, 'alwaysRejoin',
    #registry.Boolean(True, """Determines whether the bot will always try to
    #rejoin a channel whenever it's kicked from the channel."""))

conf.registerChannelValue(Shift, 'shiftSnarfer',
    registry.Boolean(True, """Determines whether the
    word all: resolves to all users."""))

conf.registerGlobalValue(Shift, 'bold',
    registry.Boolean(True, """Determines whether this plugin will bold certain
    portions of its replies."""))


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
