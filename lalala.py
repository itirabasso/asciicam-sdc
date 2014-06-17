#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mechanize
import cookielib
import sys
import urllib

def getTokenMechanize():
    br = mechanize.Browser()
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)

    br.set_handle_equiv(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False)

    # Follows refresh 0 but not hangs on refresh > 0
    br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

    # Want debugging messages?
    # br.set_debug_http(True)
    # br.set_debug_redirects(True)
    # br.set_debug_responses(True)

    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/33.0.1750.152 Chrome/33.0.1750.152 Safari/537.36')]

    r = br.open('https://developers.facebook.com/tools/explorer/')

    forms = br.forms()
    loginForm = None
    for f in br.forms():
        if f.attrs['id'] == 'login_form':
            loginForm = f

    if not loginForm: sys.exit(1)
    # # br.set_handle_refresh(False)
    loginForm['email'] = 'semana.de.la.computacion.1@gmail.com'
    loginForm['pass'] = 'aaaaaaaaaaaaa'
    loginForm.set_all_readonly(False)
    # El input submit necesita un value o mechanize no va a andar.
    loginForm.set_value("lalalala", nr=len(loginForm.controls) - 1)
    response = loginForm.click(id="u_0_1")

    r = br.open(response)
    html = r.read()

    token = html.split(',100004245942709,"')[1]
    return token[:token.index('"')]
    # print token[:token.index('"')]