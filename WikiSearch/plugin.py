###
# Copyright (c) 2012, Jonimus
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


import string
import StringIO
import urllib
import re
from wikitools import wiki, api
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks


class WikiSearch(plugins.ChannelIdDatabasePlugin):
    """Add the help for "@plugin help WikiSearch" here
    This should describe *how* to use this plugin."""
    threaded = True

    def addValidator(self, irc, apiurl):
        try:
            site = wiki.Wiki(apiurl)
        except:
            irc.error('Invalid mediawiki api.php url')


    def wiki(self, irc, msg, args, channel, id, search):
        """[<channel>] [<id>] <search term>

        Returns the first result of a search on [wikiname]. Uses default wiki
        if none specified. <channel> is only necessary if the message isn't
        sent in the channel itself.
        """

        if id is None:
            id = self.registryValue('defaultWiki')

        try:
            apiurl = self.db.get(channel, id).text
        except KeyError:
            irc.error(format('There is no wiki with id #%i.', id))
            return

        if not id:
            irc.error(format('There are no Wikis in my database ' \
                                 'for %s.', channel))

        site = wiki.Wiki(apiurl)
        params = {'action':'query',
            'list':'search',
            'srlimit':1,
            'srsearch':search,
            'srprop':'titlesnippet',
            'meta':'siteinfo',
            'siprop':'general'
        }
        req = api.APIRequest(site, params)
        res = req.query(querycontinue=False)

        if len(res['query']['search']):
            result = title =  res['query']['search'][0]['title']
        else:
            req.changeParam('srwhat','text')
            res = req.query(querycontinue=False)
            if len(res['query']['search']):
                result = title =  res['query']['search'][0]['title']
            else:
                title = 'Special:Search'
                result = 'No results Found'
        pageurl = ' '
        pageurl = res['query']['general']['server'] + res['query']['general']['articlepath']
        if not 'http' in pageurl:
            pageurl = 'http:' + pageurl
        irc.reply(result + " - " + re.sub(r'\$1', urllib.quote(title), pageurl))

    wiki = wrap(wiki, ['channeldb', optional('id'), 'text'])

Class = WikiSearch


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:



