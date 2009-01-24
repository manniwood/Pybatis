#!/usr/bin/python

# yum install python-jinja2

import psycopg2
import psycopg2.extras
import pybatis
import sys
import logging

logging.getLogger().setLevel(logging.CRITICAL)

# at app startup
conn = psycopg2.connect('user=mattertrack dbname=mattertrack')  # conn will never get opened by actual implementation
sqlMap = pybatis.SQLMap(conn, '/home/mwood/workspace/pybatis2')


#form_values = {'ID': '0', 'USERNAME': ''}
#form_values = {'USERNAME': 'mwoodclient'}
form_values = {'USERNAME': 'mwood%'}
#form_values = {'USERNAME': 'notthere'}
#form_values = {'ID': '0'}

#rows = sqlMap.select_list_of_dicts('users/select.pgsql', form_values)
rows = None
try:
    sqlMap.begin()
    rows = sqlMap.select(file='users/select.pgsql', map=form_values)
    sqlMap.commit()
except:
    print 'Exception.'
    sqlMap.rollback()
    raise
finally:
    print 'Ending.'
    sqlMap.end()

if rows == None:
    print 'Nothing found.'
else:
    for row in rows:
        print "username: ", row['USERNAME'], " password: ", row['PASSWORD']

more_rows = sqlMap.select_commit(file='users/select.pgsql', map=form_values)

if more_rows == None:
    print 'Nothing found.'
else:
    for row in more_rows:
        print "username: ", row['USERNAME'], " password: ", row['PASSWORD']


first_row = sqlMap.select_commit(file='users/select.pgsql', map=form_values, ret=pybatis.RETURN_FIRST_ROW)

if first_row == None:
    print 'Nothing found.'
else:
    print "username: ", first_row['USERNAME'], " password: ", first_row['PASSWORD']


first_item = sqlMap.select_commit(file='users/select.pgsql', map=form_values, ret=pybatis.RETURN_FIRST_DATUM)

if first_item == None:
    print 'Nothing found.'
else:
    print "username: ", first_item


# at app shutdown
conn.close()  # conn will never close in actual implementation



