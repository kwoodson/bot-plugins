###
# Copyright (c) 2014, Kenny Woodson
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

import supybot.utils as utils
from supybot.commands import *
import supybot.ircmsgs as ircmsgs
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.schedule as schedule


import sys
import datetime
import pdb
import time


class Standup(callbacks.Plugin):
    """Turn on the standup plugin by calling .Standup standup on.
    This will read the configuration out of the plugin and setup the proper
       meetings."""
    #threaded = True

    def __init__(self, irc):
        self.__parent = super(Standup, self)
        self.__parent.__init__(irc)
        self.irc = irc
        self.__standups = [
            {
                'name':     "Automation Team Standup",
                'members':  ["mmcgrath", "twiest", "mwoodson", "kwoodson", "sten", "rharriso"],
                'time':     (9, 30, 1),
                'channel':  '#libra-ops',
            },
            {
                'name':     "Ops Team Standup",
                'members':  ["mmcgrath", "agrimm", "blentz", "marek", "joel", "yocum"],
                'time':     (9, 45, 1),
                'channel':  '#libra-ops',
            },
            {
                'name':     "Release Team Standup",
                'members':  ["mmcgrath", "admiller", "tdawson", "dakini", "whearn"],
                'time':     (15, 45, 1),
                'channel':  '#libra-ops',
            },
        ]

    def _nextStandup(self,  name):
        """Calculate the timestamp of the next standup meeting"""
        t = datetime.datetime.now()
        __standup = None
        selected = [z for z in self.__standups if z["name"] == name]
        if selected:
            __standup = selected[0]
        else:
            return None

        rval = None
        hour, min, sec = __standup["time"]
        today_meeting = datetime.datetime(t.year, t.month, t.day, hour, min, sec)
        if t < today_meeting:
            rval = today_meeting
        # friday
        elif t.date().weekday() == 4:
            #schedule 72 hours
            rval = today_meeting + datetime.timedelta(days=3)
        # saturday
        elif t.date().weekday() == 5:
            #schedule 48 hours
            rval = today_meeting + datetime.timedelta(days=2)
        #elif t.day in range(5):
        else: 
            #schedule 24 hours
            rval = today_meeting + datetime.timedelta(days=1)

        #rval = (today_meeting + datetime.timedelta(seconds=60)).strftime("%s")
        return int(rval.strftime("%s"))

    def perform_standup(self):
        """Perform the daily standup"""
        # based on what time it is, guess which standup we are having
        # Which team is it?
        irc = self.irc
        now = datetime.datetime.now()
        stand_up = None
        for st in self.__standups:
            # What time is it?
            hour, min, sec = st["time"]
            if hour == now.hour and min == now.minute:
                stand_up = st
                break
        else: # did not find one
            print "Did not find a matching standup"
            return
        irc.queueMsg(ircmsgs.privmsg(stand_up["channel"], "%s -  %s - Yesterday, Today, Blocked?" % (" ".join(stand_up["members"]), stand_up["name"])))
        # schedule the next event
        next_time = self._nextStandup(stand_up["name"])
        schedule.addEvent(self.perform_standup, next_time, stand_up["name"])
        print "[Perform Standup] Scheduling standup at %s for %s" % (str(next_time), stand_up["name"])

    def standup(self, irc, msg, args, on):
        """["on"] or ["off"]

        Turn on standups
        """
        if on.lower() == "on":
            irc.reply("Standup is turned on.")
            for st in self.__standups:
                next_time = self._nextStandup(st["name"])
                try:
                  schedule.addEvent(self.perform_standup, next_time, st["name"])
                  irc.reply("Standup scheduled for %s at %s." % (st["name"], str(datetime.datetime.fromtimestamp(next_time))))
                except:
                    print sys.exc_info()
                #print "Standup scheduled at %s for %s." % (str(next_time), st["name"])
        elif on.lower() == "off":
            irc.reply("Standup is turned off.")
            schedule.schedule.reset()
        else:
            irc.reply("Standup Notifier: I don't understand [ %s ]."%on)

    standup = wrap(standup, ['text'])

    def show(self, irc, msg, args):
        """
        List currently scheduled standups
        """
        #pdb.set_trace()
        standup_names = [st['name'] for st in self.__standups]
        for item in schedule.schedule.schedule:
            if item[1] in standup_names:
                irc.reply(item[1] + " - " + str(datetime.datetime.fromtimestamp(item[0])))
    show = wrap(show)

    def remove(self, irc, msg, args, name):
        """<name>

        Team name in which to turn off a stand up.
        """
        for item in schedule.schedule.schedule:
            if item[1] == name:
                schedule.removeEvent(name)
            else:
                irc.reply("Event not found")

    remove = wrap(remove, ['text'])

    def schedule(self, irc, msg, args, timestamp, name):
        """[name] [timestamp]

        Schedule an event with [name] at [timestamp]
        """
        schedule.addEvent(self.perform_standup, int(timestamp), name)
        irc.replySuccess()

    schedule = wrap(schedule, ["int", 'text'])


Class = Standup


# wrap tutorial
# https://www.gitorious.org/supybot/supybot/source/a8d2e35fb11440e845b0ab6b9f40abe9c23a49ea:docs/USING_WRAP.rst#L122
# vim:set shiftwidth=4 softtabstop=4 expandtab
