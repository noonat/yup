import fnmatch
import logging
import os
import shutil
import urllib
import urlparse

import jinja2
import misaka
import pygments
import pygments.formatters
import pygments.lexers
import requests
import yaml

from .document import Document, iter_all


DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))

logger = logging.getLogger(__name__)


class HtmlRenderer(misaka.HtmlRenderer, misaka.SmartyPants):
    pass


class MarkdownRenderer(object):

    def __init__(self, extensions=None, flags=None):
        if extensions is None:
            extensions = (misaka.EXT_AUTOLINK |
                          misaka.EXT_FENCED_CODE |
                          misaka.EXT_NO_INTRA_EMPHASIS |
                          misaka.EXT_SPACE_HEADERS |
                          misaka.EXT_STRIKETHROUGH |
                          misaka.EXT_SUPERSCRIPT |
                          misaka.EXT_TABLES)
        if flags is None:
            flags = (misaka.HTML_ESCAPE |
                     misaka.HTML_TOC)
        self._renderer = HtmlRenderer(flags)
        self._markdown = misaka.Markdown(self._renderer, extensions)

    def render(self, text):
        return self._markdown.render(text)


def highlight(text, lang='text'):
    result = ''
    try:
        lexer = pygments.lexers.get_lexer_by_name(lang, stripall=True)
    except Exception:
        result += ('<div class="highlight"><span class="err">'
                   'Error: language "{lang}" is not supported'
                   '</span></div>').format(lang=lang)
        lexer = pygments.lexers.get_lexer_by_name('text', stripall=True)
    result += pygments.highlight(text, lexer, pygments.formatters.HtmlFormatter())
    return result


def render_all(documents, output_dir, template_filename=None,
               template_filters=None, markdown_renderer=None):
    if template_filename is None:
        template_filename = os.path.join(DATA_DIR, 'template.html')
    if markdown_renderer is None:
        markdown_renderer = MarkdownRenderer()

    template_env = jinja2.Environment(trim_blocks=True)
    template_env.filters['hl'] = highlight
    template_env.filters['md'] = (
        lambda text: markdown_renderer.render(text) if text else '')
    if template_filters:
        template_env.filters.update(template_filters)
    with open(template_filename, 'r') as f:
        template = template_env.from_string(f.read())

    if not os.path.exists(output_dir):
        logger.debug('Creating output directory %r', output_dir)
        os.mkdir(output_dir)
    try:
        shutil.copytree(os.path.join(DATA_DIR, 'css'),
                        os.path.join(output_dir, 'css'))
    except OSError as e:
        if e.errno == 17:
            logger.debug('CSS directory already exists, not creating')
        else:
            raise

    for doc in documents:
        html = template.render(doc=doc)
        output_filename = os.path.join(
            output_dir, '%s.html' % (doc.slug,))
        logger.debug('Writing %r', output_filename)
        with open(output_filename, 'w') as output_file:
            output_file.write(html)
