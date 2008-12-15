import psycopg2
import psycopg2.extras
from psycopg2.extensions import (
    ISOLATION_LEVEL_AUTOCOMMIT,
    ISOLATION_LEVEL_READ_COMMITTED,
    ISOLATION_LEVEL_SERIALIZABLE,
    STATUS_BEGIN,
    STATUS_READY)


from jinja2 import Environment, FileSystemLoader
from jinja2.runtime import Undefined

import logging

# custom Jinja tests

# detect dict val not being present
def is_present(str):
    return (not isinstance(str, Undefined)) and str != None

# detect dict val not being present or being present but empty string
def is_not_empty(str):
    return (not isinstance(str, Undefined)) and str != None and str != ''



class SQLMap(object):
    def __init__(self, conn, template_path, default_isolation_level=ISOLATION_LEVEL_READ_COMMITTED):
        self.conn = conn
        self.jinja2env = Environment(trim_blocks = True, loader = FileSystemLoader(template_path))
        self.jinja2env.tests['present'] = is_present
        self.jinja2env.tests['not_empty'] = is_not_empty
        self.default_isolation_level = default_isolation_level
        self.transaction_active = False

    def begin(self, isolation_level=None):
        # XXX: you could arguably check to see if transaction is active first
        # XXX: you could arguably check to see if cursor is still open
        conn = self.conn
        self.transaction_active = True
        if isolation_level == None:
            self.isolation_level = self.default_isolation_level
        else:
            self.isolation_level = isolation_level
        self.curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        conn.set_isolation_level(self.default_isolation_level)


    def commit(self, isolation_level=None):
        # XXX: you could arguably check to see if transaction is active first
        self.conn.commit()
        self.transaction_active = False


    def rollback(self, isolation_level=None):
        # XXX: you could arguably check to see if transaction is active first
        self.conn.rollback()
        self.transaction_active = False

    def end(self):
        self.curs.close()

    def select(self, template_pathname, map=None):
        curs = self.curs
        template = self.jinja2env.get_template(template_pathname)
        sql = template.render(map)
        curs.execute(sql, map);
        logging.debug('Just executed')
        logging.debug(curs.query)
        if curs.rowcount < 1:
            return None
        else:
            return curs.fetchall()

    def select_first_row(self, template_pathname, map=None):
        curs = self.curs
        template = self.jinja2env.get_template(template_pathname)
        sql = template.render(map)
        curs.execute(sql, map);
        if curs.rowcount < 1:
            return None
        else:
            return curs.fetchone()

    def select_first_col_of_first_row(self, template_pathname, map=None):
        curs = self.curs
        template = self.jinja2env.get_template(template_pathname)
        sql = template.render(map)
        curs.execute(sql, map);
        if curs.rowcount < 1:
            return None
        else:
            return curs.fetchone()[0]

    def insert(self, template_pathname, map=None):
        curs = self.curs
        template = self.jinja2env.get_template(template_pathname)
        sql = template.render(map)
        curs.execute(sql, map);
        return curs.statusmessage

    def update(self, template_pathname, map=None):
        curs = self.curs
        template = self.jinja2env.get_template(template_pathname)
        sql = template.render(map)
        curs.execute(sql, map);
        return curs.statusmessage


    def simple_select(self, template_pathname, map):
        rows = None
        try:
            self.begin()
            rows = self.select(template_pathname, map)
            self.commit()
        except:
            print 'Exception.'
            self.rollback()
            raise
        finally:
            print 'Ending.'
            self.end()
        return rows



