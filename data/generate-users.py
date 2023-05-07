#!/usr/bin/env python
#
# Select from groups of users and flowers according to given distributions
# Produce output in the users file format needed for recommendation model
# training.
#
import pandas as pd
import random
import time

total_records = 20000
total_users = 64
start_date = "2023-05-01T00:00:00"
end_date = "2023-05-05T00:00:00"

random.seed(0)  # always generate the same output

cheerful_flowers = [ 'common_daisy', 'daffodil', 'sunflower' ]
cheerful_weights = [ 2, 3, 5 ]

exotic_flowers = [ 'astilbe', 'bellflower', 'calendula', 'california_poppy', 'coreopsis' ]
exotic_weights = [ 1, 2, 1, 1, 2 ]

traditional_flowers  = [ 'carnation', 'iris', 'magnolia', 'rose', 'tulip' ]
traditional_weights = [ 1, 1, 2, 5, 1 ]

unusual_flowers = [ 'water_lily', 'black_eyed_susan', 'dandelion' ]
unusual_weights = [ 95, 5, 1 ]

flowers = [ 'cheerful', 'exotic', 'traditional', 'unusual' ]
flower_weights = [ 30, 25, 48, 2]

# Get a (random) date at a proportion of a range of two formatted dates.
def string_time(start, end, format, proportion):
    """
    start and end should be strings specifying times formatted in the
    given format (strftime-style), giving an interval [start, end].
    prop specifies how a proportion of the interval to be taken after
    start.  The returned time will be in the specified format.
    """
    stime = time.mktime(time.strptime(start, format))
    etime = time.mktime(time.strptime(end, format))
    ptime = stime + proportion * (etime - stime)
    return time.strftime(format, time.localtime(ptime))

def random_date(start, end, proportion):
    return string_time(start, end, '%Y-%m-%dT00:00:00', proportion)


# get plant identifiers from the catalog
catalog = pd.read_csv('flowers.catalog', header=None, names=['item', 'name', 'group'])
catalog = pd.DataFrame(catalog, columns=['item', 'name'])
catalog = dict([(n,i) for n, i in zip(catalog.name, catalog.item)])
#print(catalog)

# real work start here
plants = random.choices(flowers, flower_weights, k = total_records)
for result in plants:
    userid = random.randint(1, total_users)

    # users in first 10% of ID range only select traditional flowers
    if userid < total_users / 10:
       result = 'traditional'

    if result == 'cheerful':
       flower = random.choices(cheerful_flowers, cheerful_weights)
    elif result == 'exotic':
       flower = random.choices(exotic_flowers, exotic_weights)
    elif result == 'unusual':
       flower = random.choices(unusual_flowers, unusual_weights)
    else:
       flower = random.choices(traditional_flowers, traditional_weights)

    # Format: userid, itemid, timestamp
    itemid = catalog[flower[0]]
    datestamp = random_date(start_date, end_date, random.random())

    print("U%05d,%s,%s,Purchase" % (userid, itemid, datestamp))

