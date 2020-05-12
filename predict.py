import sys
import time
import json
from sklearn.metrics import mean_squared_error
import math

# python3 predict.py test_review.json output_itemcf.txt

start_time = time.time()

test_file = sys.argv[1]  # test_review.json
output_file = sys.argv[2]


user_dict = {}
fhand = open('user.json','r')
for line in fhand:
    temp = json.loads(line)
    user_id = temp['user_id']
    user_dict[user_id] = {}
    user_dict[user_id]['review_count'] = temp['review_count']
    user_dict[user_id]['yelping_since'] = temp['yelping_since']
    user_dict[user_id]['useful'] = temp['useful']
    user_dict[user_id]['funny'] = temp['funny']
    user_dict[user_id]['cool'] = temp['cool']
    user_dict[user_id]['fans'] = temp['fans']
    user_dict[user_id]['average_stars'] = temp['average_stars']


business_dict = {}
fhand = open('business.json','r')
for line in fhand:
    temp = json.loads(line)
    user_id = temp['business_id']
    business_dict[user_id] = {}
    business_dict[user_id]['review_count'] = temp['review_count']
    business_dict[user_id]['stars'] = temp['stars']
    business_dict[user_id]['is_open'] = temp['is_open']

output = open(output_file, "w")

fhand = open(test_file,'r')
for line in fhand:
    temp = json.loads(line)
    user_id = temp['user_id']
    business_id = temp['business_id']
    try:
        pred_u = user_dict[user_id]['average_stars']
        pred_b = business_dict[business_id]['stars']
        pred = (pred_u+pred_b)/2
    except:
        pred = 4

    output.write('{"user_id": "' + user_id + '", "business_id": "' + business_id+ '", "stars": ' + str(
        pred) + '}')
    output.write("\n")

print('Duration: ' + str(time.time() - start_time))
