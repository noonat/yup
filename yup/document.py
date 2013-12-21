import fnmatch
import json
import logging
import os
import re
import urllib
import urlparse

import requests
import yaml


logger = logging.getLogger(__name__)


class Requester(object):
    def __init__(self, url):
        self.url = url

    def join(self, path):
        return urlparse.urljoin(self.url, path)

    def request(self, method, path, **kwargs):
        return requests.request(method, self.join(path), **kwargs)


class Document(object):
    """The container for documentation parsed from a YAML file."""

    def __init__(self, requester, slug, data):
        self.slug = slug
        self.name = ' '.join([s.title() for s in slug.split('_')])
        self.description = data.get('description', '').strip()
        self.requests = [Request(requester, request)
                         for request in data['requests']]


class Request(object):
    """An individual request in the documentation.

    A request has a description, an optional list of documented parameters,
    and an optional example of the request.
    """

    non_word_re = re.compile(r'\W+')
    request_re = re.compile(r'^(GET|POST|PUT|DELETE) (.+)$')
    underscores_re = re.compile(r'^_*|_*$')

    def __init__(self, requester, data):
        self.request = data['request']
        matches = self.request_re.match(self.request)
        if not matches:
            raise Exception(('error: "{request}" must be in the format '
                             '"<method> <path>"').format(request=request))
        self.method = matches.group(1)
        self.path = matches.group(2)

        self.description = data.get('description', '').strip()
        if 'params' in data:
            if '_' in data['params']:
                params = data['params']['_'].copy()
                params.update({k: v for k, v in data['params'].iteritems()
                               if k != '_'})
            else:
                params = data['params']
            self.params = [RequestParam(k, v) for k, v in params.iteritems()]
            self.params = sorted(self.params, key=lambda r: (not r.required, r.name))
        else:
            self.params = []
        if 'example' in data:
            self.example = RequestExample(requester, self.method, self.path,
                                          data['example'])
        else:
            self.example = None

    @property
    def slug(self):
        slug = self.non_word_re.sub('_', self.request)
        slug = self.underscores_re.sub('', slug)
        return slug.lower()


class RequestParam(object):
    """A query string or form parameter for a request."""

    def __init__(self, name, data=None):
        if data is None:
            data = {}
        self.name = name
        self.type = data['type']
        self.required = data['required']
        self.description = data['description'].strip()


class RequestExample(object):
    """An example for a request.

    Examples define parameters that can be used to make a request against a
    running instance of the API being documented. The response is then captured
    and can be printed within the documentation.
    """

    def __init__(self, requester, method, path, data):
        self.method = method
        self.path = path
        if 'path' in data:
            for key, value in data['path'].iteritems():
                self.path = self.path.replace(':%s' % (key,), unicode(value))
        if 'query' in data:
            self.query = {k: json.dumps(v) if isinstance(v, (dict, list)) else v
                          for k, v in data['query'].iteritems()}
        else:
            self.query = {}
        self._requester = requester
        self._https = bool(data.get('https'))
        self._response = data.get('response')

    @property
    def response(self):
        if self._response is None:
            logger.debug('Making %s request to %s with params %r',
                         self.method, self.path, self.query)
            response = self._requester.request(self.method, self.path,
                                               params=self.query)
            try:
                self._response = response.json()
            except Exception:
                self._response = response.text()
        if isinstance(self._response, basestring):
            return self._response
        elif isinstance(self._response, dict):
            return json.dumps(self._response, sort_keys=True, indent=2)
        else:
            return self._response

    @property
    def curl(self):
        return ' \\\n> '.join(['$ curl'] + self.curl_args)

    @property
    def curl_args(self):
        args = []
        if self.method not in ('GET', 'POST'):
            args.append("-X {0}".format(self.method))
        if self.query and self.method != 'GET':
            for key, value in self.query.iteritems():
                if not isinstance(value, basestring):
                    value = json.dumps(value)
                args.append("-F '{0}={1}'".format(key, value))
        url = self._requester.join(self.path)
        if self.query and self.method == 'GET':
            url = "'" + url + "?" + urllib.urlencode(self.query) + "'"
        args.append(url)
        return args


def iter_all(input_dir, base_url, requester_cls=None):
    """Return an iterator of Document objects for YAML files in a directory."""
    if requester_cls is None:
        requester_cls = Requester
    requester = requester_cls(base_url)
    logger.debug('Looking for YAML files in %r', input_dir)
    for yaml_filename in os.listdir(input_dir):
        if not fnmatch.fnmatch(yaml_filename, '*.yaml'):
            continue
        yaml_filename = os.path.join(input_dir, yaml_filename)
        logger.debug('Reading %r', yaml_filename)
        with open(yaml_filename, 'r') as yaml_file:
            data = yaml.load(yaml_file)
        name = os.path.splitext(os.path.basename(yaml_filename))[0]
        yield Document(requester, name, data)


def load_all(input_dir, base_url, requester_cls=None):
    """Return a list of Document objects for YAML files in a directory."""
    return list(iter_all(input_dir, base_url, requester_cls))
