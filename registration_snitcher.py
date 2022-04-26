#!/usr/bin/env python


import requests
import pandas as pd
import networkx as nx
import json
import re
from collections import Counter
from datetime import datetime
from datetime import timedelta
from time import sleep
import collections
import matplotlib.pyplot as plt
import tweepy
from time import sleep
import random
import os

path = os.path.abspath(os.getcwd())

api_key = "a92e1943-c920-40fd-b2c3-18fb549b521c"

consumer_key='1PTBXSet2uW3fMcdXgyMIvnty'
consumer_secret_key='dgVyxMZvrnzJV1NNbhWlX4p74h2Qvs72iuEhUDlxobu8XoS1OU'
access_token='1516407763919900677-vAMyx53HzSz8RZ1nt5KJikxrAhSxey'
access_token_secret='koWQWvkThbBxEFMLCrblnKMHCha54M9uZctDFsu0ERjOy'

auth=tweepy.OAuthHandler(consumer_key,consumer_secret_key)
auth.set_access_token(access_token,access_token_secret)
api=tweepy.API(auth)


#PARAMETERS
time = 1 # n number of days ago to analyse - note that only 5000 registrations can be retrieved by csv. If time is large then the below limits will need to be tighter 
lower_add_limit = 2 #search for addresses that have more than n companies registered in 
upper_add_limit = 5
chart_filter = 2 #include companies on the chart that appear n or more times
creation_limit = 3 #don't create or tweet a chart if it has less than n companies
check_if_tweeted_before = True #check if there is an image already present in pwd for that address can be changed to False

reach_back = datetime.now() - timedelta(days=time)


#get csv from companies house
def get_csv():
    csv = requests.get("https://find-and-update.company-information.service.gov.uk/advanced-search/download?companyNameIncludes=&companyNameExcludes=&registeredOfficeAddress=&incorporationFromDay=" + str(reach_back.strftime('%d')) + "&incorporationFromMonth=" + str(reach_back.strftime('%m')) + "&incorporationFromYear=" + str(reach_back.strftime('%Y')) + "&incorporationToDay=" + str(datetime.now().strftime('%d')) + "&incorporationToMonth=" + str(datetime.now().strftime('%m')) + "&incorporationToYear=" + str(datetime.now().strftime('%Y')) + "&sicCodes=&dissolvedFromDay=&dissolvedFromMonth=&dissolvedFromYear=&dissolvedToDay=&dissolvedToMonth=&dissolvedToYear=")
    return csv



#make pandas dataframe from csv
def make_dataframe(csv):
    dfmd = pd.DataFrame([x.split(',') for x in csv.text.split('\n')])
    new_header = dfmd.iloc[0] #grab the first row for the header
    dfmd = dfmd[1:] #take the data less the header row
    dfmd.columns = new_header #set the header row as the df header
    
    return dfmd

#filters companies in original dataframe to only include addresses that appear between lower_add_limit and upper_add_limit
def coys_btwn(dataframe):  
    vc = dataframe['registered_office_address\r'].value_counts().to_frame()
    temp_df = vc[(vc['registered_office_address\r'] >= lower_add_limit) & (vc['registered_office_address\r'] <= upper_add_limit)]
    index_list = temp_df.index.values.tolist()
    ret_dataframe = dataframe[dataframe['registered_office_address\r'].isin(index_list)]
    
    return ret_dataframe


#gets company directors and countrys of residence from CH API
def get_directors(coynumx):
    
    director_country_list = []
    
    url = "https://api.company-information.service.gov.uk/company/" + str(coynumx[1]) + "/officers"
    response = requests.get(url, auth=(api_key, ''))
    json_search_result = response.text
    search_result = json.JSONDecoder().decode(json_search_result)

    
    for director in search_result['items']:
        try:
            director_country_list.append([director['name'], director['country_of_residence']])
        except:
            director_country_list.append([director['name'], 'BLANK'])
        
    return director_country_list


#handles passing companies to CH API
def dir_handler(sdf):
    
    coynumlist = []
    
    counter = 0
    for i, r in sdf.iterrows():
        
        try:
            coynumlist.append([r['registered_office_address\r'], r['company_name'], r['company_number'], get_directors([r['company_name'], r['company_number']])])
        except Exception as e:
            print('HTTP Error due to CH API for ' + r['company_name'] + ', continuing...')
            counter += 1
            continue
    if int((counter/len(sdf.index))*100) < 10:
        print('CH API only allows 600 requests every 5 minutes, you may have hit your rate limit')
    else:
        print('retrieved ' + str(int((counter/len(sdf.index))*100)) + '% of officers for suspicious companies')
        
    return coynumlist



#builds and saves chart
def grapher_new(dataframe, address, postcode):
    
    
    temp = dataframe.loc[dataframe['address'] == address]
    if len(temp['company_name'].unique()) > creation_limit:
        
        G = nx.Graph()
        f = plt.figure(figsize=(12, 14))
    
        for i, r in dataframe.loc[dataframe['address'] == address].iterrows():


            G.add_nodes_from([(r['company_name'], {"color": "red"})])
            G.add_nodes_from([(re.findall("[A-Z]{1,2}[0-9][A-Z0-9]? [0-9][ABD-HJLNP-UW-Z]{2}",r["address"])[0], {"color": "green"})])
            G.add_edge(r['company_name'], re.findall("[A-Z]{1,2}[0-9][A-Z0-9]? [0-9][ABD-HJLNP-UW-Z]{2}",r["address"])[0])         

            for ent in r['directors']:

                G.add_nodes_from([(ent[0], {"color": "blue"})])

                if ent[1] != "BLANK":
                    G.add_nodes_from([(ent[1], {"color": "yellow"})])

                G.add_edge(ent[0], r['company_name'])
                try:
                    G.add_edge(ent[0], ent[1])
                except:
                    continue

        color = nx.get_node_attributes(G, "color")
        color_map = []
        
        try:
            for node in G:

                if color[node] == "red":
                    color_map.append('red')
                elif color[node] == "green":
                    color_map.append('green')
                elif color[node] == "blue":
                    color_map.append('blue')
                elif color[node] == "yellow":
                    color_map.append('yellow')


            nx.draw(G, with_labels=True, font_weight='bold', node_color=color_map, ax=f.add_subplot(111))

            f.savefig(os.path.abspath(os.getcwd()) + '/' + postcode.replace(" ", "") + ".png")
            plt.close(f)

            tweeter(dataframe, address, postcode)
        except:
            print('Country of residence BLANK, skipping')            
        
    else:
        print('less than ' + str(creation_limit) + ' companies - skipping...')
        pass


#tweets chart

def tweeter(result, fc, postcode):
    
    temp = result.loc[result['address'] == fc]
    
    #print(temp)
    
    companies = len(temp['company_name'].unique())
    temp['directors'] = temp['directors'].astype(str)
    directors = len(temp['directors'].unique())
    
    space = '''
    
    
    '''
    
    tweet_text= 'There have been ' + str(directors) + " officer/s register " + str(companies) + " companies in the UK at the postcode " + str(postcode) + " detected in the last 24 hours" + space + "#OSINT #Data #opensource #joinosintbotnetwithus"
    image_path = os.path.abspath(os.getcwd()) + '/' + postcode.replace(" ", "") + ".png"

    api.update_status_with_media(tweet_text, image_path)
    
    sleep(random.randint(300, 900))



#handles errors and passes correct info to make chart
def coy_director_filterer(listoflist):
    #takes [address, company_name, company_number, [[directors]]] as input
    result = pd.DataFrame(listoflist)

    result.columns = ['address', 'company_name', 'company_number', 'directors']
    for add in result['address'].unique():
        directors_list = []
        for i, r in result.loc[result['address'] == add].iterrows():

            for ent in r['directors']:
                directors_list.append(ent[0])
        

        filtered_companies = []    
        if len ([item for item, count in collections.Counter(directors_list).items() if count >= chart_filter]) > 0:
            filtered_companies.append(r['address'])
            
        
        

        for fc in filtered_companies:

            try:
                postcode = re.findall("[A-Z]{1,2}[0-9][A-Z0-9]? [0-9][ABD-HJLNP-UW-Z]{2}",r["address"])[0]



                if check_if_tweeted_before is True:
                    try:
                        check_file = open(postcode.replace(" ", "") + ".png")


                    except Exception as e:
                        print('image not created already, starting grapher')
                        grapher_new(result, fc, postcode)

                else:
                    grapher_new(result, fc, postcode)
            except Exception as e:
                print('postcode without a space not yet handled! skipping')

def retweeter():
    for tweet in api.search_tweets(q='#joinosintbotnetwithus', count=25, lang='en'):
        try:
            print('\nRetweet Bot found tweet by @' + tweet.user.screen_name + '. ' + 'Attempting to retweet.')
            print(tweet.user.followers_count)
                      
            
            api.create_favorite(tweet.id)
            api.create_friendship(user_id=tweet.user.id)
            sleep(random.randint(10,60))
            tweet.retweet()
            sleep(random.randint(10,60))

        except tweepy.TweepyException as e:
            print('\nError. Retweet not successful. Reason: ')
            print(e)

        except StopIteration:
            break

def main():
    print('program starting...')
    coy_director_filterer(dir_handler(coys_btwn(make_dataframe(get_csv()))))
    retweeter()
    print('...complete')


if __name__ == "__main__":
    main()