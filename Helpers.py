# Term Project : Tie Strength Analysis
# Author: Ziteng Zhang
# Course: Syracuse University CIS 700: Social Media Mining
import sys
import time
from urllib2 import URLError
from httplib import BadStatusLine
import json
import io
import twitter
import networkx as nx

# define a function for login
def oauth_login():
  CONSUMER_KEY = 'Lfy0zZgD16cNvvATO5cyeQ'
  CONSUMER_SECRET = '2VWXysEFiUHXVK7nfiRkYyx5p6iR7b3SyMfA74uBg'
  OAUTH_TOKEN = '1851461396-iAzfIckgxsxamThN2NEi5SYctuAa4ALPD9we3Ib'
  OAUTH_TOKEN_SECRET = 'SCykHjOJgHQfVt3ItKHmC8XSBS6NnLWP3openfO5Fg'

  auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                           CONSUMER_KEY, CONSUMER_SECRET)

  twitter_api = twitter.Twitter(auth=auth)
  return twitter_api

# referenced from Mining the social web(2nd edition) pg.378
def make_twitter_request(twitter_api_func, max_errors=10, *args, **kw): 
    
    # A nested helper function that handles common HTTPErrors. Return an updated
    # value for wait_period if the problem is a 500 level error. Block until the
    # rate limit is reset if it's a rate limiting issue (429 error). Returns None
    # for 401 and 404 errors, which requires special handling by the caller.
    def handle_twitter_http_error(e, wait_period=2, sleep_when_rate_limited=True):
    
        if wait_period > 3600: # Seconds
            print >> sys.stderr, 'Too many retries. Quitting.'
            raise e
    
        # See https://dev.twitter.com/docs/error-codes-responses for common codes
    
        if e.e.code == 401:
            print >> sys.stderr, 'Encountered 401 Error (Not Authorized)'
            return None
        elif e.e.code == 404:
            print >> sys.stderr, 'Encountered 404 Error (Not Found)'
            return None
        elif e.e.code == 429: 
            print >> sys.stderr, 'Encountered 429 Error (Rate Limit Exceeded)'
            if sleep_when_rate_limited:
                print >> sys.stderr, "Retrying in 15 minutes...ZzZ..."
                sys.stderr.flush()
                time.sleep(60*15 + 5)
                print >> sys.stderr, '...ZzZ...Awake now and trying again.'
                return 2
            else:
                raise e # Caller must handle the rate limiting issue
        elif e.e.code in (500, 502, 503, 504):
            print >> sys.stderr, 'Encountered %i Error. Retrying in %i seconds' % \
                (e.e.code, wait_period)
            time.sleep(wait_period)
            wait_period *= 1.5
            return wait_period
        else:
            raise e

    # End of nested helper function
    
    wait_period = 2 
    error_count = 0 

    while True:
        try:
            return twitter_api_func(*args, **kw)
        except twitter.api.TwitterHTTPError, e:
            error_count = 0 
            wait_period = handle_twitter_http_error(e, wait_period)
            if wait_period is None:
                return
        except URLError, e:
            error_count += 1
            print >> sys.stderr, "URLError encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise
        except BadStatusLine, e:
            error_count += 1
            print >> sys.stderr, "BadStatusLine encountered. Continuing."
            if error_count > max_errors:
                print >> sys.stderr, "Too many consecutive errors...bailing out."
                raise

#store and load retrieved data in json format
def save_json(filename, data):
    with io.open('data/{0}.json'.format(filename), 
                 'w', encoding='utf-8') as f:
        f.write(unicode(json.dumps(data, indent=1,ensure_ascii=False)))

def load_json(filename):
    with io.open('data/{0}.json'.format(filename), 
                 encoding='utf-8') as f:
        return f.read()

#convert screen_name to id
def name_to_id(twitter_api,name):
    response = twitter_api.users.show(screen_name=name)
    return response['id']

#convert id to screen_name
def id_to_name(twitter_api,id):
    response = twitter_api.users.show(user_id=id)
    return response['screen_name']






