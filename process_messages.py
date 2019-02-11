import json
from datetime import datetime, timedelta
from dateutil import parser
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import argparse
from collections import Counter
import re

HIPCHAT_PATH_USERS = "<todo>/fitbit_history/users/"
FACEBOOK_PATH_USERS = "<todod>/facebook_history/"
ME_ID = 5173027 # My HipChat ID
FB_ME = "Dragos Costea" # My participant name in Facebook messages
MIN_WORD_LEN = 8

if __name__ == "__main__":

    argparser = argparse.ArgumentParser(description='Parse messages.')
    argparser.add_argument("other_hipchat", help="Example: dcostea")
    argparser.add_argument("other_fb", help="Example: dcostea")

    args = argparser.parse_args()

    user_hc = args.other_hipchat
    user_dir_hc = user_hc + "/"
    user_fb = args.other_fb

    word_counter_real = Counter()

    print str(datetime.now()) + " Loading HipChat JSON"
    json_file_hip = HIPCHAT_PATH_USERS + user_dir_hc + user_hc + ".json"
    f = open(json_file_hip, 'r')
    data = json.load(f)

    print str(datetime.now()) + " Finished loading HipChat JSON"


    no_hc_messages_me = 0
    no_hc_messages_other = 0

    no_words_me = 0
    no_words_other = 0
    # print data
    # For each message

    total_hc_exchanged_messages = len(data)
    print "Total no. of HipChat messages = " + str(total_hc_exchanged_messages)

    df = pd.DataFrame()
    date_list = []
    m_per_days_dict = {}

    for m in data:
        from_json = m["from"]
        from_id_field = from_json["id"]
        message_field = m["message"]
        # words = message_field.lower().split(separators)
        # for word in words:
        #    word_counter[word] += 1
        words_real = re.split('\W+', message_field.lower())
        for word in words_real:
            if (len(word) >= MIN_WORD_LEN):
                word_counter_real[word] += 1


       # print from_id_field
        if (from_id_field == ME_ID):
            no_hc_messages_me += 1
            no_words_me += len(words_real)
        else:
            no_hc_messages_other += 1
            no_words_other += len(words_real)

        date_field = m["date"]
        

        m_date = parser.parse(date_field)
        # HipChat messages are off by 2 hours behind
        m_date = m_date + timedelta(hours=2)
        # Drop microsecond support
        m_date = m_date.replace(microsecond=0)
        # Drop timezone shift 'cause it's useless anyway
        m_date = m_date.replace(tzinfo=None)

        date_list.append(m_date)
        #m_date = datetime.strptime(date_field,"%Y-%m-%dT%H:%M:%S.%z+00:00")
        #print m_date
    
    print "No. of HipChat messages sent by me = " + str(no_hc_messages_me)
    print "No. of HipChat messages sent by other = " + str(no_hc_messages_other)

    """
    df['datetime'] = date_list
    df.index = df['datetime']
    df_month = df.resample('M')
    print "dataframe:"
    print (df_month)
    """

    # print date_list
    print str(datetime.now()) + " Loading FB JSON"
    json_file_fb = FACEBOOK_PATH_USERS + user_fb + ".json"
    f_fb = open(json_file_fb, 'r')
    data_fb = json.load(f_fb)

    print str(datetime.now()) + " Finished loading FB JSON"

    participants_field = data_fb['participants']
    name_1 = participants_field[0]['name']
    #print name_1

    name_2 = participants_field[1]['name']
    #print name_2

    fb_me = ""
    fb_other = ""
    if (name_1 == FB_ME):
        fb_other = name_2
        fb_me = name_1
    elif (name_2 == FB_ME):
        fb_other = name_1
        fb_me = name_2
    else:
        print "Can't find which FB name is my name"

    messages_field = data_fb['messages']
    no_fb_messages_me = 0
    no_fb_messages_other = 0

    total_fb_exchanged_messages = len(messages_field)
    print "Total no. of FB messages " + str(total_fb_exchanged_messages)

    for m in messages_field:
        sender_name_field = m['sender_name']
        content_field = m["content"]
        # words = content_field.lower().split(separators)
        # for word in words:
        #    word_counter[word] += 1
        words_real = re.split('\W+', content_field.lower())
        for word in words_real:
            if (len(word) >= MIN_WORD_LEN):
                word_counter_real[word] += 1

        if (sender_name_field == fb_me):
            no_fb_messages_me += 1
            no_words_me += len(words_real)
        elif (sender_name_field == fb_other):
            no_fb_messages_other += 1
            no_words_other += len(words_real)
        else:
            print "Could not compare sender names"
            break

        timestamp_field = m["timestamp_ms"]
        # Need to divide by 1000 as timestamp is in ms"
        datetime_fb = datetime.fromtimestamp(timestamp_field / 1000)
        # Facebook messages are off by 10 hours behind, wtf
        datetime_fb = datetime_fb + timedelta(hours=10)
        date_list.append(datetime_fb)

    print "No. of FB messages sent by me:" + str(no_fb_messages_me)
    print "No. of FB messages sent by other:" + str(no_fb_messages_other)

    total_of_all = total_fb_exchanged_messages + total_hc_exchanged_messages
    total_of_sent_by_me = no_fb_messages_me + no_hc_messages_me
    total_of_sent_by_other = no_hc_messages_other + no_fb_messages_other

    print "Total of exchanged messages = " + str(total_of_all)
    print "Total of messages sent by me = " + str(total_of_sent_by_me)
    print "Total of messages sent by other = " + str(total_of_sent_by_other)

    f.close()
    f_fb.close()

    print "\n"
    print "Word counter real, top 10 words = "
    print word_counter_real.most_common(10)

    print "Words sent by me = " + str(no_words_me)
    print "Words sent by other = " + str(no_words_other)
    print "Words sent in total = " + str(no_words_me + no_words_other)
    """
    df = pd.DataFrame({'date': date_list})
    df['value'] = 1
    df = df.set_index('date')
    df.to_csv("mess_dates.csv")
    #df['date'] = pd.to_datetime(df['date'])
    df.index = pd.to_datetime(df.index, utc=True)
    df_g=df.groupby([(df.index.month)]).sum()

    print df_g

    
    objects_persons = ('Madi', 'Dragos')
    y_pos = np.arange(len(objects_persons))
    hc_mess = [no_hc_messages_other, no_hc_messages_me]
    fb_mess = [no_fb_messages_other, no_fb_messages_me]
    tot_mess = [total_of_sent_by_other, total_of_sent_by_me]
    
    
    plt.barh(y_pos, hc_mess, align='center', alpha=0.5)
    plt.yticks(y_pos, objects_persons)
    plt.xlabel("Total no. of HipChat messages: " + str(total_hc_exchanged_messages))
    plt.title('No. of HipChat messages by person')
    #for i, v in enumerate(objects_persons):
    #    plt.text(v, i, " "+str(v), color='blue', va='center', fontweight='bold')

    plt.savefig('hc_mess.png')

    plt.barh(y_pos, hc_mess, align='center', alpha=0.5)
    plt.yticks(y_pos, objects_persons)
    plt.xlabel("Total no of Facebook messages:" + str(total_hc_exchanged_messages))
    plt.title('No. of Facebook messages by person')
    
    plt.savefig('fb_mess.png')
    """
    print str(datetime.now()) + " Finished"
