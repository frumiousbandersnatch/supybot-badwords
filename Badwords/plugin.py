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

        # We don't call the function because replacing the string doesn't make the changes persistant.
        # We will need to use the .setValue() method to store the new string.
        # FIXME: this is not very clean.
        self.message = conf.supybot.plugins.Badwords.get("responseMessage")

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

    def add(self, irc, msg, args, channel, word):
        """[<channel>] <word>, <word>, ...

        Add one or more <word> to the word list (comma-separated).

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

        # Holds a list of ignored words. Only used for reporting.
        ignored = []
        for word in [w for w in string_to_wordlist(word) if w]:
            if word and word not in self.words[channel]:
                self.words[channel].append(word)
            else:
                ignored.append(word)

        self._save()

        if ignored:
            return irc.reply("Adding done. Ignored duplicate(s): %s" % ", ".join(ignored), private=True, notice=True)
        return irc.reply("Done adding.", private=True, notice=True)
    add = wrap(add, ['channel', 'text', 'admin'])

    def remove(self, irc, msg, args, channel, word):
        """[<channel>] <word>, <word>, ...

        Remove one or more <word> from the word list (comma-separated)."""

        # Set the channel
        if not channel in self.words:
            return irc.reply("No words are set for %r." % channel)

        # Holds a list of ignored words. Only used for reporting.
        ignored = []
        for word in [w for w in string_to_wordlist(word) if w]:
            if word in self.words[channel]:
                self.words[channel].remove(word)
            else:
                ignored.append(word)

        self._save()

        if ignored:
            return irc.reply("Removing done. Ignored unfound: %s" % ", ".join(ignored), private=True, notice=True)
        return irc.reply("Removing done.", private=True, notice=True)
    remove = wrap(remove, ['channel', 'text', 'admin'])

    def response(self, irc, msg, args, message):
        """[<message>]

        Set <messsage> as a response to bad word abusers. If <message> is not
        given, return the current message."""
        if message is not None:
            self.message.setValue(message)
        return irc.reply("Badword speakers will be responded with %r" % self.message(), private=True, notice=True)
    response = wrap(response, [optional('text'), 'admin'])

    def list(self, irc, msg, args, channel):
        """[<channel>]

        Show the list of words."""

        return irc.reply("%s: %s" % (channel, ", ".join(self.words.get(channel, []))), private=True, notice=True)
    list = wrap(list, ['channel', 'admin'])

    def clear(self, irc, msg, args, channel):
        """[<channel>]

        Clear all stored words of the current channel.
        """

        if channel in self.words:
            del self.words[channel][:]
            self._save()
        return irc.reply("All words cleared for %r." % channel, private=True, notice=True)
    clear = wrap(clear, ['channel', 'admin'])

    def clearall(self, irc, msg, args):
        """

        Clear all stored words of all channels.
        """

        self.words.clear()
        self._save()
        return irc.reply("All words cleared for all channels.", private=True, notice=True)
    clearall = wrap(clearall, ['admin'])

    def doPrivmsg(self, irc, msg):
        """This is called everytime an IRC message is recieved."""
        # Grab the actual text
        txt = msg.args[1]

        # Grab the command char
        cmd_char = conf.supybot.reply.whenAddressedBy.chars()

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
                return irc.reply(self.message, private=True, notice=True)

Class = Badwords


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
