import psycopg2
import psycopg2.extras
from psycopg2.extensions import (
    ISOLATION_LEVEL_AUTOCOMMIT,
    ISOLATION_LEVEL_READ_COMMITTED,
    ISOLATION_LEVEL_SERIALIZABLE,
    STATUS_BEGIN,
    STATUS_READY)


from jinja2 import Environment, FileSystemLoader, Template
from jinja2.runtime import Undefined

import logging

import time

########### defs

RETURN_EVERYTHING = 0
RETURN_FIRST_ROW = 1
RETURN_FIRST_DATUM = 2

########### custom Jinja tests needed by pybatis

# detect dict val not being present
def is_present(str):
    return (not isinstance(str, Undefined)) and str != None

# detect dict val not being present or being present but empty string
def is_not_empty(str):
    return (not isinstance(str, Undefined)) and str != None and str != ''

########## custom exceptions

class NullConnectionException(Exception):
    pass

class ConnectionClosedException(Exception):
    pass

class CursorAlreadyExistsException(Exception):
    pass

class CursorAlreadyOpenException(Exception):
    pass

class FileAndInlineBothNoneException(Exception):
    pass

########## utility functions

def no_op (datum):
    return datum

def row_to_dict (row, keys=None):
    if row == None:
        return None
    if keys == None:
        keys = row.keys()
    retdict = {}
    for key in keys:
        retdict[key] = row[key]
    return retdict

def rows_to_dicts (rows, keys=None):
    if rows == None:
        return None
    if len(rows) < 1:
        return None
    if keys == None:
        keys = rows[0].keys()
    retlist = []
    for row in rows:
        retlist.append(row_to_dict(row, keys))
    return retlist

def start_time_if_debug():
    if (logging.getLogger().getEffectiveLevel() == logging.DEBUG):
        return time.clock()

def elpsed_time_if_debug(the_time):
    if (logging.getLogger().getEffectiveLevel() == logging.DEBUG):
        return time.clock() - the_time

########## sql map

class SQLMap(object):
    def __init__(self, conn, template_path, default_isolation_level=ISOLATION_LEVEL_READ_COMMITTED):
        self.conn = conn
        self.jinja2env = Environment(trim_blocks = True, loader = FileSystemLoader(template_path))
        self.jinja2env.tests['present'] = is_present
        self.jinja2env.tests['not_empty'] = is_not_empty
        self.default_isolation_level = default_isolation_level
        self.curs = None
        self.template_path = template_path

    def begin(self, isolation_level=None):
        conn = self.conn
        if conn == None:
            raise NullConnectionExcepton

        if conn.closed == True:
            raise ConnectionClosedException

        if self.curs != None:
            raise CursorAlreadyExistsException

        if isolation_level == None:
            self.isolation_level = self.default_isolation_level
        else:
            self.isolation_level = isolation_level
        self.curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        conn.set_isolation_level(self.default_isolation_level)


    def commit(self, isolation_level=None):
        self.conn.commit()


    def rollback(self, isolation_level=None):
        self.conn.rollback()


    def end(self):
        self.curs.close()
        self.curs = None


    def select(self, file=None, inline=None, map=None, transformer=None, ret=RETURN_EVERYTHING):

        if file == None and inline == None:
            raise FileAndInlineBothNoneException

        if transformer == None:
            if ret == RETURN_EVERYTHING:
                transformer = rows_to_dicts
            elif ret == RETURN_FIRST_ROW:
                transformer = row_to_dict
            elif ret == RETURN_FIRST_DATUM:
                transformer = no_op

        curs = self.curs
        sql = ''

        if file != None:
            if map == None:
                # if file but no map, no need to render template; just load file directly
                # from filesystem, borrowing our jinja environment's loader to do so
                sql, filename, uptodate = self.jinja2env.loader.get_source(self.jinja2env, file)
            else:
                template = self.jinja2env.get_template(file)
                sql = template.render(map)
        else:  # use inline
            if map == None:
                # use the sql string directly; no templating to do
                sql = inline
            else:
                template = self.jinja2env.from_string(inline)
                sql = template.render(map)
        the_time = -1  # an impossible amount of time indicates time not taken
        the_time = start_time_if_debug()
        curs.execute(sql, map);
        the_time = elpsed_time_if_debug(the_time)
        logging.debug('Just executed')
        #logging.debug(curs.query)
        logging.debug('time: ' + str(the_time))
        if curs.rowcount < 1:
            return None
        else:
            if ret == RETURN_EVERYTHING:
                return transformer(curs.fetchall())
            elif ret == RETURN_FIRST_ROW:
                return transformer(curs.fetchone())
            elif ret == RETURN_FIRST_DATUM:
                return transformer(curs.fetchone()[0])


    def select_commit(self, **args):
        list_of_dicts = None
        try:
            self.begin()
            list_of_dicts = self.select(**args)
            self.commit()
        except:
            self.rollback()
            raise
        finally:
            self.end()
        return list_of_dicts


    def execute(self, file=None, inline=None, map=None):

        if file == None and inline == None:
            raise FileAndInlineBothNoneException

        curs = self.curs
        sql = ''
        if file != None:
            if map == None:
                # if file but no map, no need to render template; just load file directly
                # from filesystem, borrowing our jinja environment's loader to do so
                sql, filename, uptodate = self.jinja2env.loader.get_source(self.jinja2env, file)
            else:
                template = self.jinja2env.get_template(file)
                sql = template.render(map)
        else:  # use inline
            if map == None:
                # use the sql string directly; no templating to do
                sql = inline
            else:
                template = self.jinja2env.from_string(inline)
                sql = template.render(map)

        the_time = -1  # an impossible amount of time indicates time not taken
        the_time = start_time_if_debug()
        curs.execute(sql, map);
        the_time = elpsed_time_if_debug(the_time)
        logging.debug('Just executed')
        #logging.debug(curs.query)
        logging.debug('time: ' + str(the_time))
        return curs.statusmessage


    def execute_commit(self, **args):
        status_message = None
        try:
            self.begin()
            status_message = self.execute(**args)
            self.commit()
        except:
            self.rollback()
            raise
        finally:
            self.end()
        return status_message


