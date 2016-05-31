# Term Project : Tie Strength Analysis
# Author: Ziteng Zhang
# Course: Syracuse University CIS 700: Social Media Mining


import Helpers
import os

#get reciprocal friends from given id , max 100
def get_reciprocal_friends(id):
     
    response = Helpers.make_twitter_request(t.friends.ids,user_id=id,count=5000)
    friends = response["ids"]

    response = Helpers.make_twitter_request(t.followers.ids,user_id=id,count=5000)
    followers = response["ids"]

    reciprocal_friends =list(set(friends).intersection(set(followers)))

    return reciprocal_friends[0:100]


#oauth login
t = Helpers.oauth_login()

#root node for analysis
root_name="ptwobrussell"
root_id=Helpers.name_to_id(t,root_name)

#get all root's level_1 friends and store a list of ids to file
friends=get_reciprocal_friends(root_id)
Helpers.save_json("friend_list",friends)

#get root's timeline entities, max 100 tweets, save to file
timeline=Helpers.make_twitter_request(t.statuses.user_timeline,user_id=root_id,count=100)
Helpers.save_json("timeline_root",timeline)

#get all friends' timeline entities , max 100 tweets, save to file
for id in friends:
    print "Generate timeline for: "+str(id)
    timeline= Helpers.make_twitter_request(t.statuses.user_timeline,user_id=id,count=100)
    Helpers.save_json("timeline_"+str(id),timeline)
 
#generate name,id dictionary
id_names={}
for id in friends:
    name=Helpers.id_to_name(t,id)
    id_names[id]=name
Helpers.save_json("id_names",id_names)
