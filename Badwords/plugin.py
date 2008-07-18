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
import supybot.ircmsgs as ircmsgs
import supybot.callbacks as callbacks
import supybot.conf as conf

import re
import fnmatch

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

    def __init__(self, irc):
        self.__parent = super(Badwords, self)
        self.__parent.__init__(irc)

        # A cache for precompiled regular expression
        # regex[word] = regex
        self.regex = {}

    def add(self, irc, msg, args, channel, optlist, words):
        """[<channel>] [--kick] <word>, <word>, ...

        Add one or more words from the given <word> list (comma-separated) for
        channel <channel>. If <channel> is not given, add words for the current
        channel. If --kick is given, words will be set for user kicking.

        Support for Unix shell-style wildcards is available:
        *	matches everything.
        ?	matches any single character.
        [seq]	matches any character in seq.
        [!seq]	matches any character not in seq.

        The output of the 'list' command can also be used for mass injection
        (backup/restore).
        """

        kick = False
        for (option, arg) in optlist:
            if option == 'kick':
                kick = True

        wordlist = self.registryValue('words', channel=channel)
        kicklist = self.registryValue('kicks', channel=channel)

        for word in string_to_wordlist(words):
            if word not in wordlist:
                wordlist.append(word)
                kicklist.append(kick)
            else:
                i = wordlist.index(word)
                kicklist[i] = kick
        irc.replySuccess()
    add = wrap(add, ['channel', getopts({'kick':''}), 'text', 'admin'])

    def remove(self, irc, msg, args, channel, words):
        """[<channel>] <word>, <word>, ...

        Remove one or more words from the given <word> list (comma-separated)
        for channel <channel>. If <channel> is not given, remove words for the
        current channel.
        """

        wordlist = self.registryValue('words', channel=channel)
        kicklist = self.registryValue('kicks', channel=channel)

        for word in string_to_wordlist(words):
            if word in wordlist:
                i = wordlist.index(word)
                del wordlist[i]
                del kicklist[i]
        irc.replySuccess()
    remove = wrap(remove, ['channel', 'text', 'admin'])

    def response(self, irc, msg, args, message):
        """[<message>]

        Set <messsage> as a response to bad word abusers. If <message> is not
        given, return the current message.
        """

        if message is not None:
            self.setRegistryValue('response.string', message)
            irc.replySuccess()
        else:
            irc.reply(self.registryValue('response.string'))
    response = wrap(response, [optional('text'), 'admin'])

    def list(self, irc, msg, args, channel, optlist):
        """[<channel>] [--{kick,notice}]

        Show the list of all words for channel <channel>. If <channel> is not
        given, list all words for the current channel. If --kick is given,
        list only kicking words. If --notice is given, list only notice
        (non-kicking) words.
        """

        wordlist = self.registryValue('words', channel=channel)
        kicklist = self.registryValue('kicks', channel=channel)

        kick = None
        notice = None

        for (option, arg) in optlist:
            if option == 'kick':
                kick = True
            elif option == 'notice':
                notice = True

        # This means no option was given.
        if kick is None and notice is None:
            notice, kick = True, True

        show = []
        for i, word in enumerate(wordlist):
            kicklist[i] and kick and show.append(word)
            not kicklist[i] and notice and show.append(word)

        irc.reply("%s: %s" % (channel, ", ".join(show)), private=self.registryValue('list.asPrivate'), notice=self.registryValue('list.asNotice'))
    list = wrap(list, ['channel', getopts({'kick':'', 'notice':''}), 'admin'])

    def clear(self, irc, msg, args, channel):
        """[<channel>]

        Clear all stored words from channel <channel>. If <channel> is not
        given, clear words from the current channel.
        """

        wordlist = self.setRegistryValue('words', [], channel=channel)
        kicklist = self.setRegistryValue('kicks', [], channel=channel)
        irc.replySuccess()
    clear = wrap(clear, ['channel', 'admin'])

    # FIXME: Make this thing work when we figure out how to clear the 'words'
    # value from all channels in the registry.
#    def clearall(self, irc, msg, args):
#        """
#
#        Clear all stored words of all channels.
#        """
#
#        self.regex.clear()
#        irc.replySuccess()
#    clearall = wrap(clearall, ['admin'])

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

        wordlist = self.registryValue('words', channel=channel)
        kicklist = self.registryValue('kicks', channel=channel)

        if not wordlist:
            return

        # This is a dict containing {'word':True} as the word string and its kick value.
        words = dict(zip(wordlist, kicklist))

        for word in words:
            if not word in self.regex:
                # Clean up the word from special caracters that might make a word seen as two separate words.
                # e.g. "c'est" is seen as separate "c" and "est", which is not what we want.
                clean = re.sub("['_-]", "", word)
                # UTF strings must be converted to unicode. Then compile the regex with the re.UNICODE flag.
                # Remove the last char "$" appended by fnmatch.translate().
                regex = r"\b%s\b" % fnmatch.translate(clean.decode("utf-8"))[:-1]
                self.regex[word] = re.compile(regex, re.IGNORECASE | re.UNICODE)
            if self.regex[word].search(re.sub("['_-]", "", txt.decode("utf-8"))):
                kick = words[word]
                if kick:
                    irc.sendMsg(ircmsgs.kick(channel, msg.nick, self.registryValue('response.string')))
                else:
                    irc.reply(self.registryValue('response.string'), private=self.registryValue('response.asPrivate'), notice=self.registryValue('response.asNotice'))

Class = Badwords


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
