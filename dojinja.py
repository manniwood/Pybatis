#!/usr/bin/python

# yum install python-jinja2

import psycopg2
import psycopg2.extras

from jinja2 import Environment, FileSystemLoader
from jinja2.runtime import Undefined
jinja2env = Environment(trim_blocks = True, loader = FileSystemLoader('/home/mwood/workspace/pybatis2'))

# custom tests

# detect dict val not being present
def is_present(str):
    return (not isinstance(str, Undefined)) and str != None

# detect dict val not being present or being present but empty string
def is_not_empty(str):
    return (not isinstance(str, Undefined)) and str != None and str != ''

# custom filters

# sql escape
#def escape_sql(str):
    

jinja2env.tests['present'] = is_present

#form_values = {'ID': '0', 'USERNAME': ''}
#form_values = {'USERNAME': 'mwoodclient'}
form_values = {'USERNAME': 'mwood%'}
#form_values = {'USERNAME': 'notthere'}
#form_values = {'ID': '0'}

template = jinja2env.get_template('users/select.pgsql')
sql = template.render(form_values)
print sql

conn = psycopg2.connect('user=mattertrack dbname=mattertrack')  # conn will never get opened by actual implementation
curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
curs.execute(sql, form_values);
if curs.rowcount < 1:
    print 'Nothing found.'
else:
    rows = curs.fetchall()
    #curs.close() # sweet! rows persist even after cursor is closed!
    for row in rows:
        print "username: ", row['USERNAME'], " password: ", row['PASSWORD']
curs.close()  # our responsibility to close, including on exceptions
conn.close()  # conn will never close in actual implementation



