###
# Copyright (c) 2002-2005, Jeremiah Fincher
# Copyright (c) 2009, James Vega
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
###

import sys

import supybot.conf as conf
import supybot.ircdb as ircdb
import supybot.utils as utils
from supybot.commands import *
import supybot.ircmsgs as ircmsgs
import supybot.schedule as schedule
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import sqlite3
import collections
import urllib2
import time
import mechanize
import subprocess
import shutil
import os
import datetime

RED="\x034"
GREEN="\x033"
BLACK="\x03"

OPENSHIFT_UNAME= ''
OPENSHIFT_PASS = ''

class Shift(callbacks.PluginRegexp):
    regexps = ['shiftSnarfer']

    def __init__(self, irc):
        self.__parent = super(Shift, self)
        self.__parent.__init__(irc)
        self.irc = irc

        self.invites = {}

    def _sendMsg(self, irc, msg):
        irc.queueMsg(msg)
        irc.noReply()

    def _sendMsgs(self, irc, nicks, f):
        numModes = irc.state.supported.get('modes', 1)
        for i in range(0, len(nicks), numModes):
            irc.queueMsg(f(nicks[i:i + numModes]))
        irc.noReply()

    def shiftSnarfer(self, irc, msg, match):
        r"(^all:|^.* all:)(.*)$"
        try:
            matches = match.groups()
            author = str(msg).split("!")[0].lstrip(":")
            channel = msg.args[0]
            #L = list(irc.state.channels.values()[0].users)
            L = list(irc.state.channels[channel].users)
            L = list(set(L) - set([irc.nick, author]))
            if len(": ".join(L)) < 450:
            #L.remove(irc.nick)
            #L.remove(author)
                irc.reply("%s: %s"%(": ".join(L), "".join(matches)),  \
                          prefixNick=False)
            else:
                rep_str = ""
                while len(L) > 0:
                    if len(rep_str) + len(L[-1]) + len(": ") + \
                    len("".join(matches)) < 400:
                        rep_str = rep_str + L.pop() + ": "
                    else:
                        irc.reply("%s: %s"%(rep_str, "".join(matches)),  \
                                  prefixNick=False)
                        rep_str = ""
                else:
                    if len(rep_str) > 0:
                        irc.reply("%s: %s"%(rep_str, "".join(matches)),  \
                                  prefixNick=False)
        except:
            print sys.exc_info()
            irc.noReply()

Class = Shift

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
