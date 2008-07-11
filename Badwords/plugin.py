###
# Copyright (c) 2008, Alexandre Conrad
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
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.conf as conf

import re
import fnmatch
import cPickle
import os.path

def string_to_wordlist(words):
    """Return a list of words from the given comma-separated-string. The list can contain empty strings."""
    return [re.sub("""(^\s*?\s*|\s*?\s*$)""", "", word) for word in words.split(",")]

class Badwords(callbacks.Plugin):
    """Add the help for "@plugin help Badwords" here
    This should describe *how* to use this plugin."""
    threaded = True

    BADWORDS_DATA = os.path.join(conf.supybot.directories.data(), "badwords.pkl")

    def __init__(self, irc):
        self.__parent = super(Badwords, self)
        self.__parent.__init__(irc)

        # Loads self.words
        self._load()

    def _load(self):
        """Load the self.words dict from disk."""
        if not os.path.isfile(Badwords.BADWORDS_DATA):
            self.words = {}
            return
        f = open(Badwords.BADWORDS_DATA, "rb")
        self.words = cPickle.load(f)
        f.close()

    def _save(self):
        """Save the self.words dict to disk."""
        f = open(Badwords.BADWORDS_DATA, "wb")
        cPickle.dump(self.words, f)
        f.close()

    def _get_responseString(self): return conf.supybot.plugins.Badwords.responseString()
    def _set_responseString(self, msg): conf.supybot.plugins.Badwords.responseString.setValue(msg)
    responseString = property(_get_responseString, _set_responseString)

    def _get_responseAsNotice(self): return conf.supybot.plugins.Badwords.responseAsNotice()
    def _set_responseAsNotice(self, msg): conf.supybot.plugins.Badwords.responseAsNotice.setValue(msg)
    responseAsNotice = property(_get_responseAsNotice, _set_responseAsNotice)

    def _get_responseAsPrivate(self): return conf.supybot.plugins.Badwords.responseAsPrivate()
    def _set_responseAsPrivate(self, msg): conf.supybot.plugins.Badwords.responseAsPrivate.setValue(msg)
    responseAsPrivate = property(_get_responseAsPrivate, _set_responseAsPrivate)

    def _get_confirmResponseString(self): return conf.supybot.plugins.Badwords.confirmResponseString()
    def _set_confirmResponseString(self, msg): conf.supybot.plugins.Badwords.confirmResponseString.setValue(msg)
    confirmResponseString = property(_get_confirmResponseString, _set_confirmResponseString)

    def _get_confirmAddString(self): return conf.supybot.plugins.Badwords.confirmAddString()
    def _set_confirmAddString(self, msg): conf.supybot.plugins.Badwords.confirmAddString.setValue(msg)
    confirmAddString = property(_get_confirmAddString, _set_confirmAddString)

    def _get_confirmRemoveString(self): return conf.supybot.plugins.Badwords.confirmRemoveString()
    def _set_confirmRemoveString(self, msg): conf.supybot.plugins.Badwords.confirmRemoveString.setValue(msg)
    confirmRemoveString = property(_get_confirmRemoveString, _set_confirmRemoveString)

    def _get_confirmClearString(self): return conf.supybot.plugins.Badwords.confirmClearString()
    def _set_confirmClearString(self, msg): conf.supybot.plugins.Badwords.confirmClearString.setValue(msg)
    confirmClearString = property(_get_confirmClearString, _set_confirmClearString)

    def _get_confirmClearAllString(self): return conf.supybot.plugins.Badwords.confirmClearAllString()
    def _set_confirmClearAllString(self, msg): conf.supybot.plugins.Badwords.confirmClearAllString.setValue(msg)
    confirmClearAllString = property(_get_confirmClearAllString, _set_confirmClearAllString)

    def _get_confirmAsNotice(self): return conf.supybot.plugins.Badwords.confirmAsNotice()
    def _set_confirmAsNotice(self, msg): conf.supybot.plugins.Badwords.confirmAsNotice.setValue(msg)
    confirmAsNotice = property(_get_confirmAsNotice, _set_confirmAsNotice)

    def _get_confirmAsPrivate(self): return conf.supybot.plugins.Badwords.confirmAsPrivate()
    def _set_confirmAsPrivate(self, msg): conf.supybot.plugins.Badwords.confirmAsPrivate.setValue(msg)
    confirmAsPrivate = property(_get_confirmAsPrivate, _set_confirmAsPrivate)

    def _get_listAsNotice(self): return conf.supybot.plugins.Badwords.listAsNotice()
    def _set_listAsNotice(self, msg): conf.supybot.plugins.Badwords.listAsNotice.setValue(msg)
    listAsNotice = property(_get_listAsNotice, _set_listAsNotice)

    def _get_listAsPrivate(self): return conf.supybot.plugins.Badwords.listAsPrivate()
    def _set_listAsPrivate(self, msg): conf.supybot.plugins.Badwords.listAsPrivate.setValue(msg)
    listAsPrivate = property(_get_listAsPrivate, _set_listAsPrivate)

    def _get_channelForwarding(self): return conf.supybot.plugins.Badwords.channelForwarding()
    def _set_channelForwarding(self, msg): conf.supybot.plugins.Badwords.channelForwarding.setValue(msg)
    channelForwarding = property(_get_channelForwarding, _set_channelForwarding)

    def _get_forwardTo(self): return conf.supybot.plugins.Badwords.forwardTo()
    def _set_forwardTo(self, msg): conf.supybot.plugins.Badwords.forwardTo.setValue(msg)
    forwardTo = property(_get_forwardTo, _set_forwardTo)

    def _get_forwardString(self): return conf.supybot.plugins.Badwords.forwardString()
    def _set_forwardString(self, msg): conf.supybot.plugins.Badwords.forwardString.setValue(msg)
    forwardString = property(_get_forwardString, _set_forwardString)

    def add(self, irc, msg, args, channel, word):
        """[<channel>] <word>, <word>, ...

        Add one or more words from the given <word> list (comma-separated) for
        channel <channel>. If <channel> is not given, add words for the current
        channel.

        Support for Unix shell-style wildcards is available:
        *	matches everything.
        ?	matches any single character.
        [seq]	matches any character in seq.
        [!seq]	matches any character not in seq.

        The output of the 'list' command can also be used for mass injection
        (backup/restore).
        """

        if not channel in self.words:
            self.words[channel] = []

        for word in [w for w in string_to_wordlist(word) if w]: # filter-out potential empty strings ''
            if word not in self.words[channel]:
                self.words[channel].append(word)

        self._save()

        return irc.reply(self.confirmAddString % {"channel":channel}, private=self.confirmAsPrivate, notice=self.confirmAsNotice)
    add = wrap(add, ['channel', 'text', 'admin'])

    def remove(self, irc, msg, args, channel, word):
        """[<channel>] <word>, <word>, ...

        Remove one or more words from the given <word> list (comma-separated)
        for channel <channel>. If <channel> is not given, remove words for the
        current channel.
        """

        for word in [w for w in string_to_wordlist(word) if w]: # filter-out potential empty strings ''
            if word in self.words.get(channel, []):
                self.words[channel].remove(word)

        self._save()

        return irc.reply(self.confirmRemoveString % {"channel":channel}, private=self.confirmAsPrivate, notice=self.confirmAsNotice)
    remove = wrap(remove, ['channel', 'text', 'admin'])

    def response(self, irc, msg, args, message):
        """[<message>]

        Set <messsage> as a response to bad word abusers. If <message> is not
        given, return the current message."""
        if message is not None:
            self.responseString = message
        return irc.reply(self.confirmResponseString % {"response":self.responseString}, private=self.confirmAsPrivate, notice=self.confirmAsNotice)
    response = wrap(response, [optional('text'), 'admin'])

    def list(self, irc, msg, args, channel):
        """[<channel>]

        Show the list of words."""

        return irc.reply("%s: %s" % (channel, ", ".join(self.words.get(channel, []))), private=self.listAsPrivate, notice=self.listAsNotice)
    list = wrap(list, ['channel', 'admin'])

    def clear(self, irc, msg, args, channel):
        """[<channel>]

        Clear all stored words from channel <channel>. If <channel> is not
        given, clear words from the current channel.
        """

        if channel in self.words:
            del self.words[channel][:]
            self._save()
        return irc.reply(self.confirmClearString % {"channel":channel}, private=self.confirmAsPrivate, notice=self.confirmAsNotice)
    clear = wrap(clear, ['channel', 'admin'])

    def clearall(self, irc, msg, args):
        """

        Clear all stored words of all channels.
        """

        self.words.clear()
        self._save()
        return irc.reply(self.confirmClearAllString, private=self.confirmAsPrivate, notice=self.confirmAsNotice)
    clearall = wrap(clearall, ['admin'])

    def doPrivmsg(self, irc, msg):
        """This is called everytime an IRC message is recieved."""
        # Grab the command char
        cmd_char = conf.supybot.reply.whenAddressedBy.chars()

        # Grab the actual text
        txt = msg.args[1]

        # If it's a command, don't notify if bad words are used.
        if txt.startswith(cmd_char):
            return

        # Set the channel
        channel = msg.args[0]
        if not channel in self.words:
            return

        for word in self.words[channel]:
            # We remove the last char, which is a "$" that fnmatch.translate appends.
            regex = re.compile(r"\b%s\b" % fnmatch.translate(word)[:-1])
            if regex.search(txt.lower()):
                return irc.reply(self.responseString, private=self.responseAsPrivate, notice=self.responseAsNotice)

Class = Badwords


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
