"""Flask-debugtoolbar panel for rendering SQLAlchemy queries

Like the existing :class:`SQLAlchemyDebugPanel` but supports custom
Engine/Session objects.
"""
import time
import sys

from sqlalchemy import event
from sqlalchemy.util import ScopedRegistry
from flask import _app_ctx_stack, request, current_app, abort
from flask_debugtoolbar.panels import DebugPanel
from flask_debugtoolbar.utils import format_sql
from flask_debugtoolbar import DebugToolbarExtension
from flask_debugtoolbar import module
import itsdangerous

from jinja2 import Environment, PackageLoader


def _monkey_patch_flasksqlalchemy_panel():
    """monkey patch DebugToolbarExtension to replace sqla panel"""
    _old_default_config = DebugToolbarExtension._default_config

    def _new_default_config(instance, app):
        config = _old_default_config(instance, app)
        panels = list(config['DEBUG_TB_PANELS'])
        panels[panels.index('flask_debugtoolbar.panels.sqlalchemy.SQLAlchemyDebugPanel')] \
            = __name__ + '.SQLADebugPanel'
        config['DEBUG_TB_PANELS'] = tuple(panels)
        return config
    DebugToolbarExtension._default_config = _new_default_config


def is_select(statement):
    return statement.lower().strip().startswith('select')


def query_signer():
    return itsdangerous.URLSafeSerializer(current_app.config['SECRET_KEY'],
                                          salt='sqla-query')


def dump_query(statement, params):
    if not is_select(statement):
        return None

    try:
        return query_signer().dumps([statement, params])
    except TypeError:
        return None


def load_query(data):
    try:
        statement, params = query_signer().loads(request.args['query'])
    except (itsdangerous.BadSignature, TypeError):
        abort(406)

    # Make sure it is a select statement
    if not is_select(statement):
        abort(406)

    return statement, params


def _calling_context(app_paths):
    frm = sys._getframe(1)
    while frm.f_back is not None:
        name = frm.f_globals.get('__name__')
        for app_path in app_paths:
            if name and (name == app_path or name.startswith(app_path + '.')):
                funcname = frm.f_code.co_name
                return '%s:%s (%s)' % (
                    frm.f_code.co_filename,
                    frm.f_lineno,
                    funcname
                )
        frm = frm.f_back
    return '<unknown>'


_jinja_env = Environment(loader=PackageLoader(__name__, 'templates'))


class SQLADebugPanel(DebugPanel):
    name = 'SQL'
    _engine = None

    @classmethod
    def Configure(cls, engine, monkey_patch_debugtoolbar=True, package_names=None):
        """Configure the debug panel with an engine and session

        :param Engine engine: sqlalchemy Engine
        :param callable session: callable that returns a
        :param monkey_patch_debugtoolbar: replace existing SQLalchemy debug panel (default True)
        """
        if monkey_patch_debugtoolbar:
            _monkey_patch_flasksqlalchemy_panel()

        if package_names:
            cls.package_names = package_names
        else:
            cls.package_names = []

        cls._engine = engine
        scopefunc = _app_ctx_stack.__ident_func__
        cls._locals = ScopedRegistry(dict, scopefunc)
        event.listen(cls._engine, "before_cursor_execute", cls._before_cursor_execute)
        event.listen(cls._engine, "after_cursor_execute", cls._after_cursor_execute)

    @classmethod
    def _before_cursor_execute(cls, conn, cursor, statement, parameters, context, executemany):
        cls._locals()['QUERY_TIMER'] = time.time()

    @classmethod
    def _after_cursor_execute(cls, conn, cursor, statement, parameters, context, executemany):
        start_time = cls._locals()['QUERY_TIMER']
        end_time = time.time()
        if 'DEBUG_STATEMENTS' not in cls._locals():
            cls._locals()['DEBUG_STATEMENTS'] = []
        cls._locals()['DEBUG_STATEMENTS'].append({
            'duration': end_time - start_time,
            'sql': format_sql(statement, parameters),
            'signed_query': dump_query(statement, parameters),
            'context_long': _calling_context(cls.package_names + [current_app.import_name]),
            'context': _calling_context(cls.package_names + [current_app.import_name]),
        })

    def get_debug_queries(self):
        """Get recorded queries for current session

        This method returns the queries in a format suitable
        for use in debugging tools such as Flask-Debugtoolbar
        (with modifications)

        :return list: list of queries for this session
        """
        try:
            return self.__class__._locals()['DEBUG_STATEMENTS']
        except KeyError:
            return []

    @property
    def has_content(self):
        return bool(self.get_debug_queries())

    def process_request(self, request):
        pass

    def process_response(self, request, response):
        pass

    def nav_title(self):
        return 'SQL'

    def nav_subtitle(self):
        if self.get_debug_queries:
            count = len(self.get_debug_queries())
            return "%d %s" % (count, "query" if count == 1 else "queries")

    def title(self):
        return 'SQL queries'

    def url(self):
        return ''

    def content(self):
        queries = self.get_debug_queries()
        self.__class__._locals.clear()
        template = _jinja_env.get_template('sqla.html')
        return template.render({'queries': queries})


# Panel views
@module.route('/sqla/sql_select', methods=['GET', 'POST'])
def sqla_sql_select():
    statement, params = load_query(request.args['query'])
    engine = SQLADebugPanel._engine
    result = engine.execute(statement, params)
    template = _jinja_env.get_template('select.html')
    return template.render({
        'result': result.fetchall(),
        'headers': result.keys(),
        'sql': format_sql(statement, params),
        'duration': float(request.args['duration']),
    })


@module.route('/sqla/sql_explain', methods=['GET', 'POST'])
def sqla_sql_explain():
    statement, params = load_query(request.args['query'])
    engine = SQLADebugPanel._engine

    if engine.driver == 'pysqlite':
        query = 'EXPLAIN QUERY PLAN %s' % statement
    else:
        query = 'EXPLAIN %s' % statement

    result = engine.execute(query, params)
    template = _jinja_env.get_template('explain.html')
    return template.render({
        'result': result.fetchall(),
        'headers': result.keys(),
        'sql': format_sql(statement, params),
        'duration': float(request.args['duration']),
    })
