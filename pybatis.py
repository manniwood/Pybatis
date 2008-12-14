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

# custom Jinja tests

# detect dict val not being present
def is_present(str):
    return (not isinstance(str, Undefined)) and str != None

# detect dict val not being present or being present but empty string
def is_not_empty(str):
    return (not isinstance(str, Undefined)) and str != None and str != ''



class SQLMap(object):
    def __init__(self, conn, template_path):
        self.conn = conn
        self.jinja2env = Environment(trim_blocks = True, loader = FileSystemLoader(template_path))
        self.jinja2env.tests['present'] = is_present
        self.jinja2env.tests['not_empty'] = is_not_empty


    def select_list_of_dicts(self, template_pathname, map):
        conn = self.conn
        template = self.jinja2env.get_template(template_pathname)
        sql = template.render(map)
        curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        try:
            conn.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
            curs.execute(sql, map);
            if curs.rowcount < 1:
                return None
            else:
                return curs.fetchall()
            conn.commit()
        except:
            conn.rollback()
        finally:
            curs.close()  # our responsibility to close, including on exceptions

    # TODO: select_dict
    # TODO: select_item
    # TODO: insert
    # TODO: update
    # TODO: select_list_of_dicts, no map
    # TODO: select_dict, no map
    # TODO: select_item, no map

