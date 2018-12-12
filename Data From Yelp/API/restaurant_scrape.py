#!/usr/bin/env python

from __future__ import print_function

import json
import re
import requests
import sys
import urllib3
import signal
import MySQLdb
import logging
import pprint
#from urllib3 import HTTPError
from urllib.parse import quote
#from urllib import urlencode


API_KEY = 'Z41R0DQquIn-_Y88pmgfAoavZA_kOFv-96EtbOcnGGdPVwqik70FkOXfIy_CRlcikfZ7nuzDtbx18DYg_vKJVJs32T3x7Zgx2y1bSxNGumP2U2S6bYtPBAOig4G3W3Yx'

# API constants, you shouldn't have to change these.
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
SEARCH_PATH_BEST = '/v3/business/matches/best'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.

DEFAULT_TERM = 'dinner'
DEFAULT_LOCATION = 'San Francisco, CA'
SEARCH_LIMIT = 1

DBHOST = 'localhost'
DBUSER = 'restaurants'
DBPASS = ''
DB = 'restaurants'

LOGFILE = 'restaurants_chi.log'

rcount = 0
list_left = 0


logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    filename=LOGFILE,
                    level=logging.INFO)


def signal_handler(signal, frame):
    print('Ouch!')
    logging.info('*** killed process. completed %s entries.', rcount)
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

'''
def get_list():
    global DBHOST, DBUSER, DBPASS, DB
    print("Getting list from database")
    data = []
    Error = ""
    try:
        db = MySQLdb.connect(host=DBHOST,
                             user=DBUSER,
                             passwd=DBPASS,
                             db=DB,
                             use_unicode=True,
                             charset="utf8")
        cursor = db.cursor()
        cursor.execute('SELECT DISTINCT DBA_Name, AKA_Name, Address
                       AS Latest_Insp FROM food_inspection_chi
                       WHERE Results != 'Out of Business'
                       AND Facility_Type = "Restaurant"
                       AND Inspection_Date >= '2016-01-01'
                       GROUP BY Address;')

        row = cursor.fetchone()

        while row is not None:
            data.append(row)
            row = cursor.fetchone()
    except Error as e:
        print(e)
    finally:
        cursor.close()
        db.close()
    return data
'''

def request(host, path, api_key, url_params=None):
    """Given your API_KEY, send a GET request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        API_KEY (str): Your API Key.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % api_key,
    }

    # print(u'Querying {0} ...'.format(url))

    response = requests.request('GET', url, headers=headers, params=url_params)
    return response.json()


def business_lookup(api_key, term, address):
    global rcount
    url_params = {
        'name': name.replace(' ', '+'),
        'location': address,
        'city': "Chicago",
        'state': "IL",
        'country': "US",
    }

    return request(API_HOST, SEARCH_PATH_BEST, api_key, url_params=url_params)


def search(api_key, term, address):
    global rcount
    # term = re.sub('(?:\s\W | LLC| INC|, LLC)', ' ', term.rstrip())
    term = re.sub('(?:\s\W |#|\.|,|\d| RESTAURANT|CAFE|TAQUERIA| LLC| INC|, LLC|\([^)]*\))', ' ', term.rstrip())
    url_params = {
        'term': term.replace(' ', '+'),
        'location': address,
        'radius': "50",
        'limit': SEARCH_LIMIT
    }

    results = request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)
    # print(results)
    # print(url_params)

    try:
        if results['total'] is 0:
            print('\033[91m          not found\n\033[0m')
            logging.info('not found %s %s', term, address)
    except:
        print('whatevs')
    try:
        for value in results['businesses']:
            try:
                business_id = results['businesses'][0]['id']
            except:
                continue
            business_name = results['businesses'][0]['name']
            is_closed = results['businesses'][0]['is_closed']
            if is_closed:
                is_closed = "true"
            else:
                is_closed = "false"
            review_count = results['businesses'][0]['review_count']
            business_address1 = results['businesses'][0]['location']['address1']
            business_city = results['businesses'][0]['location']['city']
            business_state = results['businesses'][0]['location']['state']
            business_country = results['businesses'][0]['location']['country']
            business_zip = results['businesses'][0]['location']['zip_code']
            try:
                business_price = str(len(results['businesses'][0]['price']))
            except KeyError:
                business_price = "NA"
            business_rating = str(results['businesses'][0]['rating'])
            business_categories = []
            business_category0 = "NA"
            business_category1 = "NA"
            business_category2 = "NA"
            for category in results['businesses'][0]['categories']:
                business_categories.append(category['alias'])
            if len(business_categories) == 3:
                business_category0, business_category1, business_category2 = business_categories
            elif len(business_categories) == 2:
                business_category0, business_category1 = business_categories
                business_category2 = "NA"
            elif len(business_categories) == 1:
                business_category0 = business_categories[0]
                business_category1 = "NA"
                business_category2 = "NA"
            elif len(business_categories) == 0:
                business_category0 = "NA"
                business_category1 = "NA"
                business_category2 = "NA"
            business_lat = results['businesses'][0]['coordinates']['latitude']
            business_lon = results['businesses'][0]['coordinates']['longitude']

            rcount = rcount + 1
            print('\033[0m', "            adding:", '\033[92m', business_name, b'\033[93m', business_address1, '\033[0m', "\n")
            logging.info('added %s %s', business_name, business_address1)

            update_db(business_id, business_name, review_count,
                      business_address1, business_city, business_state,
                      business_country, business_zip, business_price,
                      business_rating, business_category0, business_category1,
                      business_category2, business_lat, business_lon, is_closed)
    except:
        print('business error')


def get_business(api_key, business_id):
    """Query the Business API by a business ID.
    Args:
        business_id (str): The ID of the business to query.
    Returns:
        dict: The JSON response from the request.
    """
    business_path = BUSINESS_PATH + business_id

    return request(API_HOST, business_path, api_key)

'''
def update_db(business_id, business_name, review_count, business_address1,
              business_city, business_state, business_country, business_zip,
              business_price, business_rating, business_category0,
              business_category1, business_category2, business_lat, business_lon, is_closed):
    global DBHOST, DBUSER, DBPASS, DB
    db = MySQLdb.connect(host=DBHOST,
                         user=DBUSER,
                         passwd=DBPASS,
                         db=DB,
                         use_unicode=True,
                         charset="utf8")

    cursor = db.cursor()

    cursor.execute('INSERT into restaurants_chi (id, name, review_count, address, city,
                   state, country, zip, price, rating, category0, category1,
                   category2, latitude, longitude, is_closed) VALUES (%s, %s, %s, %s, %s,
                   %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE
                   KEY UPDATE id = VALUES(id), rating = VALUES(rating),
                   latitude = VALUES(latitude), longitude = VALUES(longitude)
                   ', (business_id, business_name, review_count, business_address1,
                         business_city, business_state, business_country,
                         business_zip, business_price, business_rating,
                         business_category0, business_category1,
                         business_category2, business_lat, business_lon, is_closed))
    db.commit()
    db.close()
'''


def main():
    global list_left
    logging.info('*** starting new run.')
    #inspection_list = get_list()
    #list_left = len(inspection_list)
    logging.info('loaded %s entries from food_inspection_chi db', list_left)
    inspection_list = [["MCDONALD'S", "41.720224099058896", "-87.6433279836791"]]
    list_left = len(inspection_list)
    for dbname, akaname, address, in inspection_list:
        if akaname:
            if len(address) >= 3:
                print('\033[0m', 'searching AKA_name:', '\033[92m', akaname, '\033[93m', address, '\033[0m', list_left, 'remaining')
                logging.info('searching AKA_Name: %s %s', dbname, address)
                search(API_KEY, akaname, address)
                list_left = list_left - 1
        else:
            if len(address) >= 3:
                print('\033[0m', 'searching DBA_Name:', '\033[92m', dbname, '\033[93m', address, '\033[0m', list_left, 'remaining')
                logging.info('searching DBA_Name: %s %s', dbname, address)
                search(API_KEY, dbname, address)
                list_left = list_left - 1

                # print(dbname, latitude, longitude)
    logging.info('*** finished. completed %s entries', rcount)


if __name__ == '__main__':
    main()