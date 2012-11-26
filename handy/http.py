# -*- coding: utf-8 -*-
import re, urlparse
from httplib import HTTPConnection, _CS_IDLE


def raw_pipeline(domain, pages, max_out_bound=4, method='GET', timeout=None, debuglevel=0):
    pagecount = len(pages)
    conn = HTTPConnection(domain, timeout=timeout)
    conn.set_debuglevel(debuglevel)
    respobjs = [None] * pagecount
    finished = [False] * pagecount
    responses = [None] * pagecount
    data = [None] * pagecount
    headers = {'Host': domain, 'Content-Length': 0, 'Connection': 'Keep-Alive'}

    while not all(finished):
        # Send
        out_bound = 0
        for i, page in enumerate(pages):
            if out_bound >= max_out_bound:
                break
            elif page and not finished[i] and respobjs[i] is None:
                if debuglevel > 0:
                    print 'Sending request for %r...' % (page,)
                conn._HTTPConnection__state = _CS_IDLE # FU private variable!
                conn.request(method, page, None, headers)
                respobjs[i] = conn.response_class(conn.sock, strict=conn.strict, method=conn._method)
                out_bound += 1

        # Try to read a response
        for i, resp in enumerate(respobjs):
            if resp is None:
                continue
            if debuglevel > 0:
                print 'Retrieving %r...' % (pages[i],)
            out_bound -= 1
            skip_read = False
            resp.begin()
            if debuglevel > 0:
                print '    %d %s' % (resp.status, resp.reason)
            if 200 <= resp.status < 300:
                # Ok
                data[i] = resp.read()
                cookie = resp.getheader('Set-Cookie')
                if cookie is not None:
                    headers['Cookie'] = cookie
                skip_read = True
                finished[i] = True
                responses[i] = respobjs[i]
                respobjs[i] = None
            elif 300 <= resp.status < 400:
                # Redirect
                loc = resp.getheader('Location')
                respobjs[i] = None
                parsed = loc and urlparse.urlparse(loc)
                if not parsed:
                    # Missing or empty location header
                    data[i] = (resp.status, resp.reason)
                    finished[i] = True
                elif parsed.netloc != '' and parsed.netloc != domain:
                    # Redirect to another domain
                    data[i] = (resp.status, resp.reason, loc)
                    finished[i] = True
                else:
                    path = urlparse.urlunparse(parsed._replace(scheme='',netloc='',fragment=''))
                    if debuglevel > 0:
                        print '  Updated %r to %r' % (pages[i],path)
                    pages[i] = path
            elif resp.status >= 400:
                # Failed
                data[i] = (resp.status, resp.reason)
                finished[i] = True
                responses[i] = respobjs[i]
                respobjs[i] = None
            if resp.will_close:
                # Connection (will be) closed, need to resend
                conn.close()
                if debuglevel > 0:
                    print '  Connection closed'
                for j, f in enumerate(finished):
                    if not f and respobjs[j] is not None:
                        if debuglevel > 0:
                            print '  Discarding out-bound request for %r' % (pages[j],)
                        respobjs[j] = None
                break
            elif not skip_read:
                resp.read() # read any data
            if any(not f and respobjs[j] is None for j,f in enumerate(finished)):
                # Send another pending request
                break
        else:
            break # All respobjs are None?
    return responses, data


def pipeline(urls, **kwargs):
    url_index = dict((u, i) for i, u in enumerate(urls))
    responses, data = [None] * len(urls), [''] * len(urls)

    # Grouping urls by domain
    urls = sorted(re.match(r'http://([^/]+)(.*)$',u).groups() for u in url_index)
    groups = group(urls, 0)

    # Executing requests in each group
    for g in groups:
        pages = [url[1] for url in g]
        g_responses, g_data = raw_pipeline(g.grouper, pages, **kwargs)

        for i, page in enumerate(pages):
            url = 'http://%s%s' % (g.grouper, page)
            index = url_index[url]
            responses[index] = g_responses[i]
            data[index] = data[i]

    # Some urls may have been doubled,
    # copy responses and data for them
    if len(url_index) < len(urls):
        for i, res in enumerate(responses):
            if res is None:
                index = url_index[urls[i]]
                responses[i] = responses[index]
                data[i] = data[index]

    return responses, data


def group(object_list, key, min_group=1):
    groups = []
    group = None
    prev = None

    for obj in object_list:
        val = getattr(obj, key) if isinstance(key, str) and hasattr(obj, key) else obj[key]
        if val != prev:
            if group and len(group) < min_group:
                group.grouper += ', ' + val
            else:
                group = Group()
                group.grouper = val
                groups.append(group)
        group.append(obj)
        prev = val

    return groups


if __name__ == '__main__':
    domain = 'en.wikipedia.org:80'
    pages = ('/wiki/HTTP_pipelining', '/wiki/HTTP', '/wiki/HTTP_persistent_connection')
    data = raw_pipeline(domain, pages, debuglevel=1, method='HEAD', max_out_bound=6, timeout=1)
    for i,page in enumerate(data):
        print
        print '==== Page %r ====' % (pages[i],)
        #print page[:512]
