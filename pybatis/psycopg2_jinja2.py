# Pybatis
# Copyright 2009 Cystems Technology
# Author: Manni Wood (mwood aat cystems-tech.com)

# This file is part of Pybatis.
# 
# Pybatis is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Pybatis is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with Pybatis.  If not, see <http://www.gnu.org/licenses/>.

import pybatis

import psycopg2
import psycopg2.extras
from psycopg2.extensions import (
    ISOLATION_LEVEL_AUTOCOMMIT,
    ISOLATION_LEVEL_READ_COMMITTED,
    ISOLATION_LEVEL_SERIALIZABLE,
    STATUS_BEGIN,
    STATUS_READY)


from jinja2 import Environment, FileSystemLoader, Template

import logging

import time

########## sql map

class SQLMap(object):
    def __init__(self, conn, template_path, default_isolation_level=ISOLATION_LEVEL_READ_COMMITTED, log_behaviour=pybatis.LOG_NOTHING):
        self.conn = conn
        self.jinja2env = Environment(trim_blocks = True, loader = FileSystemLoader(template_path))
        self.jinja2env.tests['present'] = pybatis.is_present
        self.jinja2env.tests['not_empty'] = pybatis.is_not_empty
        self.default_isolation_level = default_isolation_level
        self.curs = None
        self.template_path = template_path
        self.log_behaviour = log_behaviour

    def begin(self, isolation_level=None):
        conn = self.conn
        if conn == None:
            raise pybatis.NullConnectionExcepton

        if conn.closed == True:
            raise pybatis.ConnectionClosedException

        if self.curs != None:
            raise pybatis.CursorAlreadyExistsException

        if isolation_level == None:
            self.isolation_level = self.default_isolation_level
        else:
            self.isolation_level = isolation_level
        self.curs = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)  # allows only string keys like a real dict
        conn.set_isolation_level(self.default_isolation_level)


    def commit(self, isolation_level=None):
        self.conn.commit()


    def rollback(self, isolation_level=None):
        self.conn.rollback()


    def end(self):
        self.curs.close()
        self.curs = None


    def select(self, file=None, inline=None, map={}, transformer=None, ret=pybatis.RETURN_EVERYTHING, render=True, log_debug=False):

        if file == None and inline == None:
            raise pybatis.FileAndInlineBothNoneException

        curs = self.curs
        sql = ''

        if file != None:
            if render == False:
                # As a performance enhancement, do not render template; just load file directly
                # from filesystem, borrowing our jinja environment's loader to do so
                sql, filename, uptodate = self.jinja2env.loader.get_source(self.jinja2env, file)
            else:
                template = self.jinja2env.get_template(file)
                sql = template.render(map)
        else:  # use inline
            if render == False:
                # use the sql string directly; no templating to do
                sql = inline
            else:
                template = self.jinja2env.from_string(inline)
                sql = template.render(map)
        if self.log_behaviour == pybatis.LOG_EVERYTHING or \
          (self.log_behaviour == pybatis.LOG_PER_CALL and log_debug == True):
            logging.debug('sql: ' + sql)
            the_time = -1  # an impossible amount of time indicates time not taken
            the_time = time.clock()
        curs.execute(sql, map);
        if self.log_behaviour == pybatis.LOG_EVERYTHING or \
          (self.log_behaviour == pybatis.LOG_PER_CALL and log_debug == True):
            the_time = time.clock() - the_time
            logging.debug('Just executed')
            logging.debug(curs.query)
            logging.debug('time: ' + str(the_time))
        if curs.rowcount < 1:
            return None
        else:
            if transformer == None:
                if ret == pybatis.RETURN_EVERYTHING:
                    return curs.fetchall()
                elif ret == pybatis.RETURN_FIRST_ROW:
                    # XXX: consider throwing an exception if more than one row
                    return curs.fetchone()
                elif ret == pybatis.RETURN_FIRST_DATUM:
                    # XXX: consider throwing an exception if more than one row
                    # there is only supposed to be one col in the result set,
                    # so there should only be one key!
                    # XXX: consider throwing an exception if more than one key
                    first_row = curs.fetchone()
                    keys = first_row.keys()
                    return first_row[keys[0]]
            else:
                if ret == pybatis.RETURN_EVERYTHING:
                    return transformer(curs.fetchall())
                elif ret == pybatis.RETURN_FIRST_ROW:
                    # XXX: consider throwing an exception if more than one row
                    return transformer(curs.fetchone())
                elif ret == pybatis.RETURN_FIRST_DATUM:
                    # XXX: consider throwing an exception if more than one row
                    # there is only supposed to be one col in the result set,
                    # so there should only be one key!
                    # XXX: consider throwing an exception if more than one key
                    first_row = curs.fetchone()
                    keys = first_row.keys()
                    return transformer(first_row[keys[0]])


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


    def execute(self, file=None, inline=None, map={}, render=True, log_debug=False):

        if file == None and inline == None:
            raise pybatis.FileAndInlineBothNoneException

        curs = self.curs
        sql = ''
        if file != None:
            if render == False:
                # As a performance enhancement, do not render template; just load file directly
                # from filesystem, borrowing our jinja environment's loader to do so
                sql, filename, uptodate = self.jinja2env.loader.get_source(self.jinja2env, file)
            else:
                template = self.jinja2env.get_template(file)
                sql = template.render(map)
        else:  # use inline
            if render == False:
                # use the sql string directly; no templating to do
                sql = inline
            else:
                template = self.jinja2env.from_string(inline)
                sql = template.render(map)
        if self.log_behaviour == pybatis.LOG_EVERYTHING or \
          (self.log_behaviour == pybatis.LOG_PER_CALL and log_debug == True):
            logging.debug('sql: ' + sql)
            the_time = -1  # an impossible amount of time indicates time not taken
            the_time = time.clock()
        curs.execute(sql, map);
        if self.log_behaviour == pybatis.LOG_EVERYTHING or \
          (self.log_behaviour == pybatis.LOG_PER_CALL and log_debug == True):
            the_time = time.clock() - the_time
            logging.debug('Just executed')
            logging.debug(curs.query)
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


