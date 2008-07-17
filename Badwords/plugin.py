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
    """Return a list of words from the given comma-separated-string."""
    wordlist = []
    for word in words.split(","):
        word = re.sub("""(^\s*?\s*|\s*?\s*$)""", "", word)
        word and wordlist.append(word)
    return wordlist

class Badwords(callbacks.Plugin):
    """Add the help for "@plugin help Badwords" here
    This should describe *how* to use this plugin."""
    threaded = True

    BADWORDS_DATA = os.path.join(conf.supybot.directories.data(), "badwords.pkl")

    def __init__(self, irc):
        self.__parent = super(Badwords, self)
        self.__parent.__init__(irc)

        # Loads self.words from disk.
        self.load()

        # A cache for precompiled regular expression
        # regex[word] = regex
        self.regex = {}

    def load(self):
        """Load the self.words from disk."""
        if not os.path.isfile(Badwords.BADWORDS_DATA):
            self.words = {}
            return
        f = open(Badwords.BADWORDS_DATA, "rb")
        self.words = cPickle.load(f)
        f.close()

    def save(self):
        """Save the self.words to disk."""
        f = open(Badwords.BADWORDS_DATA, "wb")
        cPickle.dump(self.words, f)
        f.close()

    def _get_responseString(self): return conf.supybot.plugins.Badwords.response.string()
    def _set_responseString(self, msg): conf.supybot.plugins.Badwords.response.string.setValue(msg)
    responseString = property(_get_responseString, _set_responseString)

    def _get_responseAsNotice(self): return conf.supybot.plugins.Badwords.response.asNotice()
    def _set_responseAsNotice(self, msg): conf.supybot.plugins.Badwords.response.asNotice.setValue(msg)
    responseAsNotice = property(_get_responseAsNotice, _set_responseAsNotice)

    def _get_responseAsPrivate(self): return conf.supybot.plugins.Badwords.response.asPrivate()
    def _set_responseAsPrivate(self, msg): conf.supybot.plugins.Badwords.response.asPrivate.setValue(msg)
    responseAsPrivate = property(_get_responseAsPrivate, _set_responseAsPrivate)

    def _get_confirmationResponse(self): return conf.supybot.plugins.Badwords.confirmation.response()
    def _set_confirmationResponse(self, msg): conf.supybot.plugins.Badwords.confirmation.setValue(msg)
    confirmationResponse = property(_get_confirmationResponse, _set_confirmationResponse)

    def _get_confirmationAdd(self): return conf.supybot.plugins.Badwords.confirmation.add()
    def _set_confirmationAdd(self, msg): conf.supybot.plugins.Badwords.confirmation.add.setValue(msg)
    confirmationAdd = property(_get_confirmationAdd, _set_confirmationAdd)

    def _get_confirmationRemove(self): return conf.supybot.plugins.Badwords.confirmation.remove()
    def _set_confirmationRemove(self, msg): conf.supybot.plugins.Badwords.confirmation.remove.setValue(msg)
    confirmationRemove = property(_get_confirmationRemove, _set_confirmationRemove)

    def _get_confirmationClear(self): return conf.supybot.plugins.Badwords.confirmation.clear()
    def _set_confirmationClear(self, msg): conf.supybot.plugins.Badwords.confirmation.clear.setValue(msg)
    confirmationClear = property(_get_confirmationClear, _set_confirmationClear)

    def _get_confirmationClearAll(self): return conf.supybot.plugins.Badwords.confirmation.clearAll()
    def _set_confirmationClearAll(self, msg): conf.supybot.plugins.Badwords.confirmation.clearAll.setValue(msg)
    confirmationClearAll = property(_get_confirmationClearAll, _set_confirmationClearAll)

    def _get_confirmationAsNotice(self): return conf.supybot.plugins.Badwords.confirmation.asNotice()
    def _set_confirmationAsNotice(self, msg): conf.supybot.plugins.Badwords.confirmation.asNotice.setValue(msg)
    confirmationAsNotice = property(_get_confirmationAsNotice, _set_confirmationAsNotice)

    def _get_confirmationAsPrivate(self): return conf.supybot.plugins.Badwords.confirmation.asPrivate()
    def _set_confirmationAsPrivate(self, msg): conf.supybot.plugins.Badwords.confirmation.asPrivate.setValue(msg)
    confirmationAsPrivate = property(_get_confirmationAsPrivate, _set_confirmationAsPrivate)

    def _get_listingAsNotice(self): return conf.supybot.plugins.Badwords.listing.asNotice()
    def _set_listingAsNotice(self, msg): conf.supybot.plugins.Badwords.listing.asNotice.setValue(msg)
    listingAsNotice = property(_get_listingAsNotice, _set_listingAsNotice)

    def _get_listingAsPrivate(self): return conf.supybot.plugins.Badwords.listing.asPrivate()
    def _set_listingAsPrivate(self, msg): conf.supybot.plugins.Badwords.listing.asPrivate.setValue(msg)
    listingAsPrivate = property(_get_listingAsPrivate, _set_listingAsPrivate)

    def _get_forwardingEnabled(self): return conf.supybot.plugins.Badwords.forwarding.enabled()
    def _set_forwardingEnabled(self, msg): conf.supybot.plugins.Badwords.forwarding.enabled.setValue(msg)
    forwardingEnabled = property(_get_forwardingEnabled, _set_forwardingEnabled)

    def _get_forwardingChannels(self): return conf.supybot.plugins.Badwords.forwarding.channels()
    def _set_forwardingChannels(self, msg): conf.supybot.plugins.Badwords.forwarding.channels.setValue(msg)
    forwardingChannels = property(_get_forwardingChannels, _set_forwardingChannels)

    def _get_forwardingString(self): return conf.supybot.plugins.Badwords.forwarding.string()
    def _set_forwardingString(self, msg): conf.supybot.plugins.Badwords.forwarding.string.setValue(msg)
    forwardingString = property(_get_forwardingString, _set_forwardingString)

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

        for word in string_to_wordlist(word):
            if word not in self.words[channel]:
                self.words[channel].append(word)

        self.save()

        return irc.reply(self.confirmationAdd % {"channel":channel}, private=self.confirmationAsPrivate, notice=self.confirmationAsNotice)
    add = wrap(add, ['channel', 'text', 'admin'])

    def remove(self, irc, msg, args, channel, word):
        """[<channel>] <word>, <word>, ...

        Remove one or more words from the given <word> list (comma-separated)
        for channel <channel>. If <channel> is not given, remove words for the
        current channel.
        """

        for word in string_to_wordlist(word):
            if word in self.words.get(channel, []):
                self.words[channel].remove(word)

        self.save()

        return irc.reply(self.confirmationRemove % {"channel":channel}, private=self.confirmationAsPrivate, notice=self.confirmationAsNotice)
    remove = wrap(remove, ['channel', 'text', 'admin'])

    def response(self, irc, msg, args, message):
        """[<message>]

        Set <messsage> as a response to bad word abusers. If <message> is not
        given, return the current message.
        """
        if message is not None:
            self.responseString = message
        return irc.reply(self.confirmationResponse % {"response":self.responseString}, private=self.confirmationAsPrivate, notice=self.confirmationAsNotice)
    response = wrap(response, [optional('text'), 'admin'])

    def list(self, irc, msg, args, channel):
        """[<channel>]

        Show the list of words.
        """

        return irc.reply("%s: %s" % (channel, ", ".join(self.words.get(channel, []))), private=self.listingAsPrivate, notice=self.listingAsNotice)
    list = wrap(list, ['channel', 'admin'])

    def clear(self, irc, msg, args, channel):
        """[<channel>]

        Clear all stored words from channel <channel>. If <channel> is not
        given, clear words from the current channel.
        """

        if channel in self.words:
            del self.words[channel][:]
            self.save()
        return irc.reply(self.confirmationClear % {"channel":channel}, private=self.confirmationAsPrivate, notice=self.confirmationAsNotice)
    clear = wrap(clear, ['channel', 'admin'])

    def clearall(self, irc, msg, args):
        """

        Clear all stored words of all channels.
        """

        self.words.clear()
        self.save()
        return irc.reply(self.confirmationClearAll, private=self.confirmationAsPrivate, notice=self.confirmationAsNotice)
    clearall = wrap(clearall, ['admin'])

    def doPrivmsg(self, irc, msg):
        """This is called everytime an IRC message is recieved."""
        # Grab the actual text
        txt = msg.args[1]

        # Don't process bot commands.
        cmd_char = conf.supybot.reply.whenAddressedBy.chars()
        if txt.startswith(cmd_char):
            return

        # Do we have any words for the channel?
        channel = msg.args[0]
        if not channel in self.words:
            return

        for word in self.words[channel]:
            if not word in self.regex:
                # Clean up the word from special caracters that might make a word seen as two separate words.
                # e.g. "c'est" is seen as separate "c" and "est", which is not what we want.
                clean = re.sub("['_-]", "", word.decode("utf-8"))
                # UTF strings must be converted to unicode. Then compile the regex with the re.UNICODE flag.
                # Remove the last char "$" appended by fnmatch.translate().
                regex = r"\b%s\b" % fnmatch.translate(clean)[:-1]
                self.regex[word] = re.compile(regex, re.IGNORECASE | re.UNICODE)
            if self.regex[word].search(re.sub("['_-]", "", txt.decode("utf-8"))):
                return irc.reply(self.responseString, private=self.responseAsPrivate, notice=self.responseAsNotice)

Class = Badwords


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
