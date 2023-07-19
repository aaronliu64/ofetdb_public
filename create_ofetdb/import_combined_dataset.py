# %% Import Libraries

import pandas as pd
import numpy as np
import psycopg2 as pg
import os
from psycopg2.extras import Json
from psycopg2.extensions import AsIs
import functools
import json
import sys

# %% Helper Functions

# import requests
# import bibtexparser
import pprint

# Postgres python
from psycopg2.extras import Json

def addapt_numpy_float64(numpy_float64):
    return AsIs(numpy_float64)

def addapt_numpy_int64(numpy_int64):
    return AsIs(numpy_int64)

def nan_to_null(f,
        _NULL=AsIs('NULL'),
        _Float=pg.extensions.Float):
    if not np.isnan(f):
        return _Float(f)
    return _NULL

pg.extensions.register_adapter(np.float64, addapt_numpy_float64)
pg.extensions.register_adapter(np.int64, addapt_numpy_int64)
pg.extensions.register_adapter(float, nan_to_null)

param_dict = {
    "host"      : "127.0.0.1",
    "database"  : "ofetdb_testenv",
    "user"      : "postgres",
    "password"  : "Rahul2411!", #your  password here
    "port"      : "5432",
}

def connect(params_dict):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # connect to the PostgreSQL server
#         print('Connecting to the PostgreSQL database...')
        conn = pg.connect(**params_dict)
    except (Exception, pg.DatabaseError) as error:
        print(error)
        sys.exit(1) 
#     print("Connection successful")
    return conn

# def doi2dict(doi):
#     #create url
#     url = "http://dx.doi.org/" + doi
    
#     #create dictionary of http bibtex headers that requests will retrieve from the url
#     headers = {"accept": "application/x-bibtex"}
    
#     #reqeusts information specified by bibtex from url
#     r = requests.get(url, headers = headers).text    
    
#     #parse the returned bibtex text to a dictionary
#     #NOTE: USE bibtexparser.customization to split strings into list, etc. (https://bibtexparser.readthedocs.io/en/master/bibtexparser.html?highlight=bparser#module-bibtexparser.bparser)
#     bibdata = bibtexparser.bparser.BibTexParser().parse(r)
    
#     # # print doi metadata
#     # pp = pprint.PrettyPrinter(indent=4)
#     # pp.pprint(bibdata.entries[0])
    
#     #return dict of metadata
#     return bibdata.entries[0]

def row_to_json(a):
    
    """Takes a Series object as an input, with columns in dot notation according to 
    ofetdb schema, converts to a json formatted dict. Must use Excel literature/expt template with dot notation"""

    output = {}
    for key, value in a.iteritems():
        if pd.isnull(value) == False: #Only add key:value if not empty in the json
            path = key.split('.')
            target = functools.reduce(lambda d, k: d.setdefault(k, {}), path[:-1], output)
            target[path[-1]] = value
    return output

# %% Insert Processes

fname = 'combined/combined_seed_data.xlsx'
sheetnames = pd.ExcelFile(fname).sheet_names[2:]
# data = {key:None for key in sheetnames}

for SN in sheetnames:
    sheet = pd.read_excel(fname, sheet_name=SN)
    print('Inserting tuples into {}...'.format(SN))
    for i, row in sheet.iterrows():
        entry = row_to_json(row)

        for key in entry.keys():
            if type(entry[key])==dict:
                entry[key]=Json(entry[key])
        
#         print(entry)
        conn = connect(param_dict)
        cur = conn.cursor()
        
        columns = entry.keys()
        values = [entry[column] for column in columns]
        sql = 'insert into %s (%s) values %s ON CONFLICT DO NOTHING'

        try:
            cur.execute(sql, (AsIs(SN), AsIs(','.join(columns)), tuple(values)) )
            conn.commit()
#             print("Operation Successful")
        except (Exception, pg.DatabaseError) as error:
            print("Error: %s" % error)
            conn.rollback()
        
        cur.close()
        conn.close()
    print("Operation Successful")
# sheet = data[sheetnames[0]]

# %% Insert Measurements

fname = 'combined/combined_measurements.xlsx'
sheetnames = pd.ExcelFile(fname).sheet_names


for SN in sheetnames:
    sheet = pd.read_excel(fname, sheet_name=SN)
    print('Inserting tuples from {} into MEASUREMENT...'.format(SN))
    for i, row in sheet.iterrows():
        entry = row_to_json(row)
    
        for key in entry.keys():
            if type(entry[key])==dict:
                entry[key]=Json(entry[key])
    
    #         print(entry)
        conn = connect(param_dict)
        cur = conn.cursor()
    
        columns = entry.keys()
        values = [entry[column] for column in columns]
        sql = 'insert into measurement (%s) values %s ON CONFLICT DO NOTHING'
    
        try:
            cur.execute(sql, (AsIs(','.join(columns)), tuple(values)) )
            conn.commit()
    #             print("Operation Successful")
        except (Exception, pg.DatabaseError) as error:
            print("Error: %s" % error)
            conn.rollback()
            
            cur.close()
            conn.close()
        
    print("Operation Successful")
    
