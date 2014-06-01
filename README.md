# flask-debugtoolbar SQLAlchemy Panel

This is an extension panel for the excellent
[flask-debugtoolbar](http://flask-debugtoolbar.readthedocs.org/en/latest/) that
records and displays SQLAlchemy queries. It is based heavily on the existing
SQLAlchemy toolbar that comes with flask-debugtoolbar but does not require the
Flask-SQLAlchemy extension. Instead it is configured with an existing `Engine`

The motivation for this panel is the fact that the existing debug toolbar
requires the flask-sqlalchemy extension to be used. Some applications may prefer
to configure and manage the SQLAlchemy engine on their own or may be
integrating with existing applications/libraries that do not use flask-sqlalchemy.

**NOTE:** If you are using the
[flask-sqlalchemy](https://github.com/mitsuhiko/flask-sqlalchemy) flask
extension already you do **not** need this as flask-debugtoolbar already has a panel
for debugging queries.

## Install

```sh
$ pip install fdt-sqlalchemy
```

## Usage

```python
from fdtsqlalchemy import SQLADebugPanel
...
# later configure the panel *before* debug toolbar extension
if app.debug:
    SQLADebugPanel.Configure(engine)
    DebugToolbarExtension(app)
```

## Options

The `Configure` classmethod accepts an SQLAlchemy `Engine`, with which it records
queries issued by your application. This engine should be valid at configure
time which means, if necessary, you should configure your database code before
calling this method.

The `Configure` classmethod accepts two optional arguments:

* `monkey_patch_debugtoolbar` (default True) - Replace the default SQLAlchemy
  panel in flask-debugtoolbar with this one. If set to False you'll need to
  manually configure flask-debugtoolbar with the `DEBUG_TB_PANELS` option.
* `package_names` (default None) - list of additional package names to check to
  determine the calling context of your queries. These will be searched, in
  order, in addition to your apps `import_name`. This argument is useful if your
  application makes queries in packages other than the packages configured for
  your flask app. Example: `SQLADebugPanel.Configure(engine,
  package_names=['myapp', 'someotherapp'])`

