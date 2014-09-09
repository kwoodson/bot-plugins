
"""
Basic commands for openshift.
"""

import supybot
import supybot.world as world

# Use this for the version of this plugin.  You may wish to put a CVS keyword
# in here if you\'re keeping the plugin in CVS or some similar system.
__version__ = "%%VERSION%%"

__author__ = supybot.authors.kwoodson

# This is a dictionary mapping supybot.Author instances to lists of
# contributions.
__contributors__ = {
    #supybot.authors.skorobeus: ['enable', 'disable'],
    }

import config
import plugin
reload(plugin) # In case we're being reloaded.

if world.testing:
    import test

Class = plugin.Class
configure = config.configure
