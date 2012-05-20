# encoding=utf-8

import os, argparse, sys
from threading import local

from jinja2 import TemplateNotFound, FileSystemLoader, Environment
# this is a workaround for a snow leopard bug that babel does not
# work around :)
if os.environ.get('LC_CTYPE', '').lower() == 'utf-8':
    os.environ['LC_CTYPE'] = 'en_US.utf-8'

from datetime import datetime
from babel import dates, numbers, support, Locale
from babel.messages.frontend import parse_mapping
from babel.util import pathmatch

_language = None
_active = local()


def activate_locale(locale):
    _active.value = locale

def get_locale():
    return _active.value


def get_translations():
    """Returns the correct gettext translations that should be used for
    this request.  This will never fail and return a dummy translation
    object if used outside of the request or if a translation cannot be
    found.
    """
    translations = support.Translations.load(cli.catalog, [get_locale()])
    return translations


def gettext(string, **variables):
    """Translates a string with the current locale and passes in the
    given keyword arguments as mapping to a string formatting string.

    ::

        gettext(u'Hello World!')
        gettext(u'Hello %(name)s!', name='World')
    """
    t = get_translations()
    if t is None:
        return string % variables
    return t.ugettext(string) % variables
_ = gettext


def ngettext(singular, plural, num, **variables):
    """Translates a string with the current locale and passes in the
    given keyword arguments as mapping to a string formatting string.
    The `num` parameter is used to dispatch between singular and various
    plural forms of the message.  It is available in the format string
    as ``%(num)d`` or ``%(num)s``.  The source language should be
    English or a similar language which only has one plural form.

    ::

        ngettext(u'%(num)d Apple', u'%(num)d Apples', num=len(apples))
    """
    variables.setdefault('num', num)
    t = get_translations()
    if t is None:
        return (singular if num == 1 else plural) % variables
    return t.ungettext(singular, plural, num) % variables


def pgettext(context, string, **variables):
    """Like :func:`gettext` but with a context.
    """
    t = get_translations()
    if t is None:
        return string % variables
    return t.upgettext(context, string) % variables


def npgettext(context, singular, plural, num, **variables):
    """Like :func:`ngettext` but with a context.
    """
    variables.setdefault('num', num)
    t = get_translations()
    if t is None:
        return (singular if num == 1 else plural) % variables
    return t.unpgettext(context, singular, plural, num) % variables


def translations():
    """Returns a list of all the locales translations exist for.  The
    list returned will be filled with actual locale objects and not just
    strings. A no-op translation is added for the `default_locale`.
    """
    if not os.path.isdir(cli.catalog):
        return []
    result = set([Locale.parse(cli.baselocale)])
    for folder in os.listdir(cli.catalog):
        locale_dir = os.path.join(cli.catalog, folder, 'LC_MESSAGES')
        if not os.path.isdir(locale_dir):
            continue
        if filter(lambda x: x.endswith('.mo'), os.listdir(locale_dir)):
            result.add(Locale.parse(folder))
    return result


def context():
    return dict(
        now=datetime.now(),
        current_locale=get_locale(),
        locales=translations(),
    )

def write_template(name, folder=None):
    target = cli.output
    if folder:
        target = os.path.join(target, folder)
    if not os.path.isdir(target):
        os.makedirs(target)
    with open(os.path.join(target, name), 'w') as fp:
        template = env.get_template(name)
        fp.write(template.render(**context()).encode('utf-8'))

        
parser = argparse.ArgumentParser()
parser.add_argument('--verbose', '-v', action='count')
parser.add_argument('--output', '-o', default='public/')
parser.add_argument('--catalog', '-c', default='translations/')
parser.add_argument('--templates', '-t', default='app/assets/')
parser.add_argument('--babelconf', '-b', default='babel.cfg')
parser.add_argument('--baselocale', default='en')

cli = parser.parse_args()


def guess_autoescape(template_name):
    if template_name is None or '.' not in template_name:
        return False
    ext = template_name.rsplit('.', 1)[1]
    return ext in ('html', 'htm', 'xml')

env = Environment(autoescape=guess_autoescape,
                  loader=FileSystemLoader(cli.templates),
                  extensions=['jinja2.ext.autoescape', 'jinja2.ext.i18n'])
env.install_gettext_callables(
    lambda x: get_translations().ugettext(x),
    lambda s, p, n: get_translations().ungettext(s, p, n),
    newstyle=True
)


def main():
    
    try:
        mappings, _ = parse_mapping(open(cli.babelconf))
    except IOError:
        sys.exit("Could not find Babel conf ({0})".format(cli.babelconf))
    
    search_paths = [search_path for (search_path, _) in mappings]
    
    def is_template(name):
        full_name = os.path.join(cli.templates, name)
        for path in search_paths:
            if pathmatch(path, full_name):
                return True
        
    for locale in translations():
        activate_locale(locale)
        if cli.verbose:
            print "Processing locale:", get_locale()
        for name in env.list_templates():
            if not is_template(name):
                continue
            folder = get_locale().language
            if cli.verbose > 1:
                print "Writing template: ", name
            write_template(name, folder)
