#! /usr/bin/env python


import re
import urllib2
import base64

import collectd


class Nginx(object):
    def __init__(self):
        self.pattern = re.compile("([A-Z][\w]*).+?(\d+)")
        self.urls = {}

    def do_nginx_status(self):
        for instance, (url, user, pswd) in self.urls.items():
            try:
		request = urllib2.Request(url)
		base64string = base64.encodestring('%s:%s' % (user, pswd)).replace('\n', '')
		request.add_header("Authorization", "Basic %s" % base64string)
                response = urllib2.urlopen(request)
            except urllib2.HTTPError, e:
                collectd.error(str(e))
            except urllib2.URLError, e:
                collectd.error(str(e))
            else:
                data = response.read()
                m = self.pattern.findall(data)
                for key, value in m:
                    metric = collectd.Values()
                    metric.plugin = 'nginx-%s' % instance
                    metric.type_instance = key.lower()
                    metric.type = 'nginx_connections'
                    metric.values = [value]
                    metric.dispatch()

                requests = data.split('\n')[2].split()[-1]
                collectd.debug('Requests %s' % requests)
                metric = collectd.Values()
                metric.plugin = 'nginx-%s' % instance
                metric.type = 'nginx_requests'
                metric.values = [requests]
                metric.dispatch()

    def config(self, obj):
        self.urls = dict((node.key, node.values) for node in obj.children)


nginx = Nginx()
collectd.register_config(nginx.config)
collectd.register_read(nginx.do_nginx_status)
