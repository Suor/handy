# -*- coding: utf-8 -*-
import re


__all__ = ['StripWhitespace']


class StripWhitespace(object):
    """
    Strips leading and trailing whitespace from response content.
    """
    NEWLINE_RE = re.compile(r'>\s*\n\s*<')
    SPACES_RE = re.compile(r'>\s{2,}<')

    def process_response(self, request, response):
        if response['Content-Type'].startswith('text/html'):
            content = response.content
            content = self.NEWLINE_RE.sub('>\n<', content)
            content = self.SPACES_RE.sub('> <', content)
            response.content = content
        return response
