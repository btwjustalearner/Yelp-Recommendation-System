import time
import sys
import pandas as pd
import json
import math
import statistics
import time
import xgboost as xgb
import pickle
from collections import Counter


start_time = time.time()

test_file = sys.argv[1]  # test_review.json
output_file = sys.argv[2]

model_file1 = 'xgb1.model'
model_file2 = 'xgb2.model'


# businessavg_file = 'business_avg.json'
# useravg_file = 'user_avg.json'
# train_file = 'train_review.json'
# user_file = 'user.json'
# business_file = 'business.json'

businessavg_file = '../resource/asnlib/publicdata/business_avg.json'
useravg_file = '../resource/asnlib/publicdata/user_avg.json'
train_file = '../resource/asnlib/publicdata/train_review.json'
user_file = '../resource/asnlib/publicdata/user.json'
business_file = '../resource/asnlib/publicdata/business.json'


with open(businessavg_file,'r') as f:
    bavg_dict = json.loads(f.read())

with open(useravg_file,'r') as f:
    uavg_dict = json.loads(f.read())

user_dict = {}
fhand = open(user_file, 'r')
for line in fhand:
    temp = json.loads(line)
    user_id = temp['user_id']
    user_dict[user_id] = {}
    user_dict[user_id]['years'] = 2020 - int(temp['yelping_since'][:4])
    user_dict[user_id]['useful'] = temp['useful'] / 100
    user_dict[user_id]['funny'] = temp['funny'] / 100
    user_dict[user_id]['cool'] = temp['cool'] / 100
    user_dict[user_id]['fans'] = temp['fans'] / 100
    user_dict[user_id]['friends'] = len(temp['friends'].split(',')) / 100
    user_dict[user_id]['compliment_hot'] = temp['compliment_hot'] / 100
    user_dict[user_id]['compliment_more'] = temp['compliment_more'] / 100
    user_dict[user_id]['compliment_profile'] = temp['compliment_profile'] / 100
    user_dict[user_id]['compliment_cute'] = temp['compliment_cute'] / 100
    user_dict[user_id]['compliment_list'] = temp['compliment_list'] / 100

    user_dict[user_id]['compliment_note'] = temp['compliment_note'] / 100
    user_dict[user_id]['compliment_plain'] = temp['compliment_plain'] / 100
    user_dict[user_id]['compliment_cool'] = temp['compliment_cool'] / 100
    user_dict[user_id]['compliment_funny'] = temp['compliment_funny'] / 100
    user_dict[user_id]['compliment_writer'] = temp['compliment_writer'] / 100
    user_dict[user_id]['compliment_photos'] = temp['compliment_photos'] / 100
    user_dict[user_id]['friends_list'] = temp['friends'].split(', ')


business_dict = {}
fhand = open(business_file,'r')
for line in fhand:
    temp = json.loads(line)
    user_id = temp['business_id']
    business_dict[user_id] = {}
    business_dict[user_id]['is_open'] = temp['is_open']
    categories = temp['categories']
    if 'Food' in categories or 'Restaurant' in categories:
        business_dict[user_id]['restaurant'] = 1
    else:
        business_dict[user_id]['restaurant'] = 0
    try:
        bike = temp['attributes']['BikeParking']
        if bike == 'True':
            business_dict[user_id]['bike'] = 1
        else:
            business_dict[user_id]['bike'] = 0
    except:
        pass
    try:
        lat = temp['latitude']
        long = temp['longitude']
        if (lat > 36.08) & (lat < 36.17) & (long > -115.21) & (long < -115.15):
            business_dict[user_id]['strip'] = 1
        else:
            business_dict[user_id]['strip'] = 0
    except:
        pass

b2u_dict = {}
fhand = open(train_file, 'r')
for line in fhand:
    temp = json.loads(line)
    star = temp['stars']
    user_id = temp['user_id']
    business_id = temp['business_id']
    if business_id in b2u_dict:
        b2u_dict[business_id][user_id] = star
    else:
        b2u_dict[business_id] = {}
        b2u_dict[business_id][user_id] = star


bavg_list = []
uavg_list = []

years_list = []
fans_list = []
friends_list = []

useful_list = []
funny_list = []
cool_list = []

hot_list = []
more_list = []
profile_list = []
cute_list = []
clist_list = []
note_list = []
plain_list = []
ccool_list = []
cfunny_list = []
writer_list = []
photos_list = []

isopen_list = []
restaurant_list = []
bike_list = []
strip_list = []

mean_fr_rating_list = []
mode_fr_rating_list = []
count_fr_rating_list = []

u_list = []
b_list = []


def mode_func(L):
    if len(L)>0:
         counter = Counter(L)
         max_count = max(counter.values())
         modes = [item for item, count in counter.items() if count == max_count]
         if len(modes)==1:
             return modes[0]
         else:
             return None
    else:
        return None


fhand = open(test_file, 'r')
for line in fhand:
    temp = json.loads(line)
    user_id = temp['user_id']
    business_id = temp['business_id']
    u_list.append(user_id)
    b_list.append(business_id)
    try:
        bavg = bavg_dict[business_id]
        bavg_list.append(bavg)
    except:
        bavg_list.append(None)
    try:
        uavg = uavg_dict[user_id]
        uavg_list.append(uavg)
    except:
        uavg_list.append(None)

    try:
        years = user_dict[user_id]['years']
        years_list.append(years)
    except:
        years_list.append(None)
    try:
        fans = user_dict[user_id]['fans']
        fans_list.append(fans)
    except:
        fans_list.append(None)
    try:
        friends = user_dict[user_id]['friends']
        friends_list.append(friends)
    except:
        friends_list.append(None)
    try:
        useful = user_dict[user_id]['useful']
        useful_list.append(useful)
    except:
        useful_list.append(None)

    try:
        funny = user_dict[user_id]['funny']
        funny_list.append(funny)
    except:
        funny_list.append(None)

    try:
        cool = user_dict[user_id]['cool']
        cool_list.append(cool)
    except:
        cool_list.append(None)
    try:
        hot = user_dict[user_id]['compliment_hot']
        hot_list.append(hot)
    except:
        hot_list.append(None)

    try:
        more = user_dict[user_id]['compliment_more']
        more_list.append(more)
    except:
        more_list.append(None)
    try:
        profile = user_dict[user_id]['compliment_profile']
        profile_list.append(profile)
    except:
        profile_list.append(None)
    try:
        cute = user_dict[user_id]['compliment_cute']
        cute_list.append(cute)
    except:
        cute_list.append(None)
    try:
        clist = user_dict[user_id]['compliment_list']
        clist_list.append(clist)
    except:
        clist_list.append(None)
    try:
        note = user_dict[user_id]['compliment_note']
        note_list.append(note)
    except:
        note_list.append(None)
    try:
        plain = user_dict[user_id]['compliment_plain']
        plain_list.append(plain)
    except:
        plain_list.append(None)
    try:
        ccool = user_dict[user_id]['compliment_cool']
        ccool_list.append(ccool)
    except:
        ccool_list.append(None)
    try:
        cfunny = user_dict[user_id]['compliment_funny']
        cfunny_list.append(cfunny)
    except:
        cfunny_list.append(None)
    try:
        writer = user_dict[user_id]['compliment_writer']
        writer_list.append(writer)
    except:
        writer_list.append(None)
    try:
        photos = user_dict[user_id]['compliment_photos']
        photos_list.append(photos)
    except:
        photos_list.append(None)
    try:
        isopen = business_dict[business_id]['is_open']
        isopen_list.append(isopen)
    except:
        isopen_list.append(None)

    try:
        restaurant = business_dict[business_id]['restaurant']
        restaurant_list.append(restaurant)
    except:
        restaurant_list.append(None)
    try:
        bike = business_dict[business_id]['bike']
        bike_list.append(bike)
    except:
        bike_list.append(None)
    try:
        strip = business_dict[business_id]['strip']
        strip_list.append(strip)
    except:
        strip_list.append(None)
    try:
        ufriendsl = user_dict[user_id]['friends_list']
        ufrratingsl = []
        for friend_id in ufriendsl:
            try:
                ufrratingsl.append(b2u_dict[business_id][friend_id])
            except:
                pass
        count_fr_rating_list.append(len(ufrratingsl))
        try:
            mean_fr_rating_list.append(statistics.mean(ufrratingsl))
        except:
            mean_fr_rating_list.append(None)
        try:
            mode_fr_rating_list.append(mode_func(ufrratingsl))
        except:
            mode_fr_rating_list.append(None)
    except:
        mean_fr_rating_list.append(None)
        mode_fr_rating_list.append(None)
        count_fr_rating_list.append(None)

test = pd.DataFrame()
test['bavg'] = bavg_list
test['uavg'] = uavg_list

test['years'] = years_list
test['fans'] = fans_list
test['friends'] = friends_list

test['useful'] = useful_list
test['funny'] = funny_list
test['cool'] = cool_list


test['hot'] = hot_list
test['more'] = more_list
test['profile'] = profile_list
test['cute'] = cute_list
test['clist'] = clist_list
test['note'] = note_list
test['plain'] = plain_list
test['ccool'] = ccool_list
test['cfunny'] = cfunny_list
test['writer'] = writer_list
test['photos'] = photos_list


test['isopen'] = isopen_list
test['restaurant'] = restaurant_list
test['bike'] = bike_list
test['strip'] = strip_list

test['mean_fr_rating'] = mean_fr_rating_list
test['mode_fr_rating'] = mode_fr_rating_list
test['count_fr_rating'] = count_fr_rating_list



xgb_model1 = pickle.load(open(model_file1, "rb"))
xgb_model2 = pickle.load(open(model_file2, "rb"))
# ['bavg','uavg','isopen','years','fans','useful','hot','friends']

test.fillna(value=pd.np.nan, inplace=True)

test1 = test[test['uavg'].notnull()]
test2 = test[test['uavg'].isnull()]

preds1 = xgb_model1.predict(test1[['mean_fr_rating','mode_fr_rating','restaurant','bike','bavg','uavg','isopen'
    ,'years','fans','useful','funny','cool','photos','friends','hot']])
preds11 = [max(1.3, min(4.95, x+0.008)) for x in preds1]
test1['preds'] = preds11

preds2 = xgb_model2.predict(test2[['mean_fr_rating','mode_fr_rating','restaurant','bike','bavg','uavg','isopen'
    ,'years','fans','useful','funny','cool','photos','friends','hot']])
preds21 = [max(1.7, min(4.8, x)) for x in preds2]
test2['preds'] = preds21

result = pd.concat([test1, test2])
result.sort_index(inplace=True)
preds = result['preds']

output = open(output_file, "w")

for i in range(len(test)):
    output.write('{"user_id": "' + str(u_list[i]) + '", "business_id": "' + str(b_list[i]) + '", "stars": ' + str(preds[i]) + '}')
    output.write("\n")

print('Duration: ' + str(time.time() - start_time))