# -*- coding: utf-8 -*-
import re

class StripWhitespace(object):
    """
    Strips leading and trailing whitespace from response content.
    """
    def process_response(self, request, response):
        if response['Content-Type'].startswith('text/html'):
            content = response.content
            content = re.sub(r'>\s*\n\s*<', '>\n<', content)
            content = re.sub(r'>\s{2,}<', '> <', content)
            response.content = content
        return response
