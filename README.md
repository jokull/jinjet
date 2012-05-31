jinjet
------

Static generator for Jinja2 templates with localized site tree at `/<language>`
for each localization. The output is static and deployable. I created this script because I missed Jinja2 block based templating and the
Babel localization framework when using HTML5 frontend assemblers. 

Code is adapted from Armin Ronacher's Flask-Babel extensions.

Install
-------

`$ pip install git+git://github.com/jokull/jinjet.git`

Using jinjet
------------

I'm using [brunch](http://brunch.io) to assemble the frontend. This guide will
assume the same, but you can use this for any directory of templates to generate
a static localized site tree.

Brunch has the concept of *assets*, a folder of stuff that doesn't need to be
compiled or processed. Assets are copied to the root of the output directory on
generation. For this guide we'll render from the asset directory and output to
the public folder just like Brunch. 

First create some templates:

    $ tree app/assets
    .
    ├── hi.html
    └── index.html

`hi.html` is a template that extends `index.html`.

    {% extends "index.html" %}

    {% block content %}
      {{ _('Hi') }}! {{ now.year }}
    {% endblock %}

Consult the Jinja template documentation for more information on extending
blocks and the syntax.

### Translations

We're going to use the excellent pybabel utility to manage translation catalogs.
It will need a mapping file to search for translation strings.

    $ cat babel.cfg
    [jinja2: **/assets/**.html]
    extensions=jinja2.ext.autoescape,jinja2.ext.with_

Extract the translation strings into `messages.pot`:

    $ pybabel extract -F babel.cfg -o messages.pot .

Create a locale for each additional language inside a `translations` directory:

    $ pybabel init -i messages.pot -d translations -l de

Now edit the translations/de/LC_MESSAGES/messages.po file as needed. Compile the
translation into a gettext catalog file (.mo):

    $ pybabel compile -d translations

Consult the Babel documentation if you are lost.

### Running jinjet

Now run jinjet over the asset directory with the same output path as brunch. It
will override the `public` directory with rendered versions of the same
templates in the default locale, and a subdirectory for each additional locale.

    $ jinjet -v
    Processing locale: de
    Processing locale: en

`jinjet --help` will show you some options, mostly for directory names.

Let's see what jinjet generated.

    $ tree public/
    public/
    ├── hi.html
    ├── index.html
    ├── de
    │   ├── hi.html
    │   └── index.html
    ├── en
    │   ├── hi.html
    │   └── index.html
    ├── javascripts
    │   ├── app.js
    │   └── vendor.js
    └── stylesheets
        └── app.css
    
    
If you look at `public/de/hi.html` you should see the template, extended from
`index.html` with the strings translated. Jinja2 block based templating and
Babel translation FTW. The root templates are left intact so you might want to
redirect from the root to a default locale in the server conf. Jinja2 HTML
templates are not pretty in the browser.

Template Context
----------------

jinjet renders all templates with this context for you to play with.

+ `now`: `datetime.datetime.now()` 
+ `current_locale`: The current `<Locale>` object
+ `locales`: List of all available locales

The locale object has some useful properties, namely `language`, `display_name`
and tools to get the right scientific formatting and localized date strings.
Loop over `locales` to display a list of available language translations on your
site:

    <div class="language-picker">
      {% for locale in locales if locale != current_locale %}
      <a href="/{{ locale.language }}/" class="btn">{{ locale.display_name }}</a>
      {% endfor %}
    </div>

Missing Features
----------------

+ Output a CoffeeScript translation catalog for all locales, or compiled Eco and
  Handlebars templates for all locales.
+ Add date and currency template filters like Flask-Babel.

Changelog
---------

### 0.2.1

+ Run without translations catalog; useful for using Jinja2 features but not 
  translated sites.

### 0.2

+ `--watch`

### 0.1

+ Initial Release

