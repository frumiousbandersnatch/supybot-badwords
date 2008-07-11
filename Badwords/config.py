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

import supybot.conf as conf
import supybot.registry as registry

def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('Badwords', True)


Badwords = conf.registerPlugin('Badwords')
# This is where your configuration variables (if any) should go.  For example:
conf.registerGroup(Badwords, "response")
conf.registerGlobalValue(Badwords.response, 'string', registry.String("PLEASE, USE A MORE APPROPRIATE VOCABULARY!", """The response message returned to the user when a word is used."""))
conf.registerGlobalValue(Badwords.response, 'asNotice', registry.Boolean(True, """The response returned as notice."""))
conf.registerGlobalValue(Badwords.response, 'asPrivate', registry.Boolean(True, """The response returned as private."""))

# Confirmation messages
conf.registerGroup(Badwords, "confirmation")
conf.registerGlobalValue(Badwords.confirmation, 'response', registry.String("Message response set: '%(response)s'", """The confirmation message returned when adding words."""))
conf.registerGlobalValue(Badwords.confirmation, 'add', registry.String("Word(s) added for %(channel)s.", """The confirmation message returned when adding words."""))
conf.registerGlobalValue(Badwords.confirmation, 'remove', registry.String("Word(s) removed for %(channel)s.", """The confirmation message returned when removing words."""))
conf.registerGlobalValue(Badwords.confirmation, 'clear', registry.String("All words cleared for %(channel)s.", """The confirmation message returned when clearing words."""))
conf.registerGlobalValue(Badwords.confirmation, 'clearAll', registry.String("All words cleared for all channels.", """The confirmation message returned when clearing words of all channels."""))
conf.registerGlobalValue(Badwords.confirmation, 'asNotice', registry.Boolean(True, """The confirmation message returned as notice."""))
conf.registerGlobalValue(Badwords.confirmation, 'asPrivate', registry.Boolean(True, """The confirmation message returned as private."""))

# Listing
conf.registerGroup(Badwords, "listing")
conf.registerGlobalValue(Badwords.listing, 'asNotice', registry.Boolean(True, """The word listing returned as notice."""))
conf.registerGlobalValue(Badwords.listing, 'asPrivate', registry.Boolean(True, """The word listing returned as private."""))

# Forwarding
conf.registerGroup(Badwords, "forwarding")
conf.registerGlobalValue(Badwords.forwarding, 'enabled', registry.Boolean(False, """Enables channel forwarding if set to True."""))
conf.registerGlobalValue(Badwords.forwarding, 'channels', registry.SpaceSeparatedListOfStrings([], """A space-separated list of channels."""))
conf.registerGlobalValue(Badwords.forwarding, 'string', registry.String("User %(nick)s from %(channel)s said: %(message)s", """The forwarding message sent to channels."""))


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
