import json
import math
import pandas as pd
import statistics
import time
import xgboost as xgb
import pickle
import numpy as np
from collections import Counter

start_time = time.time()


model1_file = 'xgb1.model'
model2_file = 'xgb2.model'


# train_file = 'train_review.json'
# businessavg_file = 'business_avg.json'
# useravg_file = 'user_avg.json'
# business_file = 'business.json'
# user_file = 'user.json'

train_file = '../resource/asnlib/publicdata/train_review.json'
businessavg_file = '../resource/asnlib/publicdata/business_avg.json'
useravg_file = '../resource/asnlib/publicdata/user_avg.json'
business_file = '../resource/asnlib/publicdata/business.json'
user_file = '../resource/asnlib/publicdata/user.json'



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


with open(businessavg_file,'r') as f:
    bavg_dict = json.loads(f.read())

with open(useravg_file,'r') as f:
    uavg_dict = json.loads(f.read())


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

# with open(aggbusiness_file,'r') as f:
#     business_dict = json.loads(f.read())
#
# with open(agguser_file,'r') as f:
#     user_dict = json.loads(f.read())
#
# with open(binfo_file,'r') as f:
#     binfo_dict = json.loads(f.read())
#
# with open(uinfo_file,'r') as f:
#     uinfo_dict = json.loads(f.read())
#
# with open(businessavg_file,'r') as f:
#     bavg_dict = json.loads(f.read())
#
# with open(useravg_file,'r') as f:
#     uavg_dict = json.loads(f.read())


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

truth_list = []


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


fhand = open(train_file, 'r')
for line in fhand:
    temp = json.loads(line)
    star = temp['stars']
    truth_list.append(star)
    user_id = temp['user_id']
    business_id = temp['business_id']
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

train = pd.DataFrame()
train['truth'] = truth_list
train['bavg'] = bavg_list
train['uavg'] = uavg_list

train['years'] = years_list
train['fans'] = fans_list
train['friends'] = friends_list

train['useful'] = useful_list
train['funny'] = funny_list
train['cool'] = cool_list


train['hot'] = hot_list
train['more'] = more_list
train['profile'] = profile_list
train['cute'] = cute_list
train['clist'] = clist_list
train['note'] = note_list
train['plain'] = plain_list
train['ccool'] = ccool_list
train['cfunny'] = cfunny_list
train['writer'] = writer_list
train['photos'] = photos_list


train['isopen'] = isopen_list
train['restaurant'] = restaurant_list
train['bike'] = bike_list
train['strip'] = strip_list

train['mean_fr_rating'] = mean_fr_rating_list
train['mode_fr_rating'] = mode_fr_rating_list
train['count_fr_rating'] = count_fr_rating_list

train.fillna(value=pd.np.nan, inplace=True)

train1 = train[train['uavg'].notnull()]
train2 = train[train['uavg'].isnull()]

xgb_model = xgb.XGBRegressor(
    booster='gbtree',
    objective = 'reg:linear',
    eval_metric='rmse',
    gamma=0.1,
    min_child_weight = 1,
    max_depth = 5,
    subsample= 0.8,
    colsample_bytree= 0.9,
    tree_method= 'exact',
    learning_rate=0.1,
    n_estimators=90,
    nthread=4,
    scale_pos_weight=1,
    seed=27
    )

bst1 = xgb_model.fit(train1[['mean_fr_rating','mode_fr_rating','restaurant'
                                  ,'bike','bavg','uavg','isopen','years'
                                  ,'fans','useful','funny','cool','photos','friends'
                                  ,'hot']], train1['truth'])

pickle.dump(bst1, open(model1_file, "wb"))

xgb_model = xgb.XGBRegressor(
    booster='gbtree',
    objective = 'reg:linear',
    eval_metric='rmse',
    gamma=0.1,
    min_child_weight = 1,
    max_depth = 5,
    subsample= 0.8,
    colsample_bytree= 0.9,
    tree_method= 'exact',
    learning_rate=0.1,
    n_estimators=90,
    nthread=4,
    scale_pos_weight=1,
    seed=27
    )

bst2 = xgb_model.fit(train2[['mean_fr_rating','mode_fr_rating','restaurant'
                                  ,'bike','bavg','uavg','isopen','years'
                                  ,'fans','useful','funny','cool','photos','friends'
                                  ,'hot']], train2['truth'])

pickle.dump(bst2, open(model2_file, "wb"))

print('Duration: ' + str(time.time() - start_time))

