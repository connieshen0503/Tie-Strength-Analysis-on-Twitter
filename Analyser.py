import os
import Helpers
import json
import string
import prettytable

root_name="ptwobrussell"

#oauth login
t = Helpers.oauth_login()

#load json data
data=Helpers.load_json("timeline_root")
timeline=json.loads(data)
data=Helpers.load_json("friend_list")
friendlist=json.loads(data)
#print friendlist

#use dictionary inside dictionary to demonstrate id attributes
#which include mentioned_count(by root)
#              mention_count(mention root)
#              reply_count
#              retweet_count
#              mutual_hashtags
id_info_dict={}
data=Helpers.load_json("id_names")
id_names=json.loads(data)

for item in friendlist:

    id_info_dict[item]={'mentioned_count':0,
                        'mention_count':0,
                        'reply_count':0,
                        'retweet_count':0,
                        'mutual_hashtags':[],
                        'screen_name':id_names[str(item)],
                        'id':item}
    
'''
Analyse root timeline,collect useful informations:
mentioned_count,retweet_count andgenerate root
hashtags list for later comparing
'''

#Collect ids mentioned by root
for tweet in timeline:
    mentions= tweet['entities']['user_mentions']
    for item in mentions:
        id=item['id']
        if(id in friendlist):
            id_info_dict[id]['mentioned_count']+=1
#print json.dumps(id_info_dict,indent=1)
            
#Collect retweets ids
for tweet in timeline:
    if tweet['retweeted']==True :
        print "Retweeted:"
        print json.dumps(tweet,indent=1)
        response=Helpers.make_twitter_request(t.statuses.retweeters.ids,id=tweet['id'])
        for id in response:
            if(id in friendlist):
                id_info_dict[id]['retweet_count']+=1
#print json.dumps(id_info_dict,indent=1)               

#Collect root hashtags
root_hashtags=[]
for tweet in timeline:
    hashtags=tweet['entities']['hashtags']
    for item in hashtags:
        ht=item['text']
        root_hashtags.append(ht)
#print root_hashtags

'''
Analyse level-1 reciprocal friends' timelines,
collect information to calculate mention_count,reply_count
and generate each node's hashtag list
'''

#file list to traverse from
file_list=[]
for id in friendlist:
    file_list.append("timeline_"+str(id))
#print file_list
#Analyse each id's timeline
for file in file_list:
    data=Helpers.load_json(file)
    timeline=json.loads(data)
    #sometimes timeline entities may contain nothing due to protection
    if timeline:
        for tweet in timeline:
            id=tweet['user']['id']
            if tweet['in_reply_to_screen_name']==root_name:
                id_info_dict[id]['reply_count']+=1
            mentions=tweet['entities']['user_mentions']
            for item in mentions:
                if item['screen_name']==root_name:
                    id_info_dict[id]['mention_count']+=1
            hashtags=tweet['entities']['hashtags']
            for ht in hashtags:
                tag=ht['text']
                if tag in root_hashtags:
                    if tag not in id_info_dict[id]['mutual_hashtags']:
                        id_info_dict[id]['mutual_hashtags'].append(tag)
            
   
#print json.dumps(id_info_dict,indent=1)

#present findings
#All nodes' statistics
#Use prettytable package to do output
#build columns

print "Statistics of Reciprocal Friends of ptwobrussell: "
print "Note: mention_count refers to the times that this user mentioned ptwobrussell,"
print "      mentioned_count refers to the times that this user was mentioned by ptwobrussell."
x=prettytable.PrettyTable(["screen_name","user_id","mention_count","mentioned_count",
                           "Reply(s)","Retweet(s)","Mutual Interests"])
#adjust alignign
x.align["Screen_name"] = "l" 
x.padding_width = 1

#add rows
id_attributes=id_info_dict.values()
for item in id_attributes:
    tags=""
    #handle list to string values to present common interests
    for tag in item['mutual_hashtags']:
        tags=tags+"  "+str(tag)
    row=[item['screen_name'],item['id'],item['mention_count'],
         item['mentioned_count'],item['reply_count'],item['retweet_count'],
         tags]
    x.add_row(row)
print x


