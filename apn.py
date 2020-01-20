import requests
import sys
import yaml
import re
import time
import unicodedata
import traceback
import json
from models import *
from constants import *
from maps import *

errors = []

def add_trailing_zero(pb):
    return "{:.2f}".format(float(pb))

def load_tiers():
    with open('li_test.yaml', 'r') as f:
        li = yaml.load(f)
    return li["line_items"]

def load_creative_sizes():
    with open('li_test.yaml', 'r') as f:
        creatives = yaml.load(f)
    return creatives["creatives"]["sizes"]

def populate_map(type, tier, id):
    if type not in pb_map:
        pb_map[type] = {
            tier: id
        }
    else:
        pb_map[type].update({
            tier: id
        })

def normalize(string):
    return unicodedata.normalize('NFKD', string).encode('utf-8', 'ignore')

def make_auth(user, passwd):
    return {"auth":{"username":user,"password":passwd}}

def get_auth():
    url = 'https://api.appnexus.com/auth'
    data = json.dumps(make_auth(APN_USER, APN_PASS))
    auth = requests.post(url, data=data)
    return unicodedata.normalize('NFKD', auth.json()["response"]["token"]).encode('utf-8', 'ignore')

def api_wrapper(call_type, url, auth, data=None):
    data_send = json.dumps(data)
    result = api_call(call_type, url, auth, data_send)
    if result is False:
        return False
    result_data = result.json()
    print('response data ', result_data)

    try:
        if result_data["response"]:
            if "status" in result_data["response"]:
                if result_data["response"]["status"] == "OK":
                    print('api response is OK!')
                    return result_data["response"]
            elif "error_code" in result_data["response"]:
                if result_data["response"]["error_code"] == "RATE_EXCEEDED":
                    print('rate limit hit.. trying again..')
                    # handles exceeded rate limit issue
                    # will call itself recusively till result is received or just return False
                    retry_after_time = result_data["response"]["error_code"]["dbg_info"]["write_limit_seconds"]
                    time.sleep(retry_after_time)
                    api_wrapper("post", url, auth, data)
            else:
                #log it
                errors.append(result_data["response"])
                print('Error code received from APN ', result_data)
                return False
        else:
            #log it
            errors.append(result_data["response"])
            print('Error in API call ', result_data)
            return False
    except:
        print('Error in api_wrapper ', traceback.format_exc())
        return False

def api_call(call_type, url, auth, data=None):
    try:
        request_method = getattr(requests, call_type)
        response = request_method(url, headers=auth, data=data)
        return response
    except:
        print('Error in api_call ', traceback.format_exc())
        return False

def creatives(sizes, auth, creative_url, creative_data):
    print('trafficking creatives...')
    creatives = []
    for index, size in enumerate(sizes):
        current_size = re.split(r"x",sizes[index])
        creative_send = creative_data
        creative_send["creative"]["template"]["id"] = 5
        creative_send["creative"]["width"] = current_size[0]
        creative_send["creative"]["height"] = current_size[1]
        creative_send["creative"]["name"] = f'PBjs_HB_{current_size[0]}x{current_size[1]}'
        creative = api_wrapper("post", creative_url, auth, creative_send)
        print('creative is here! ', creative)
        if creative is not False:
            populate_map("creatives", f'{current_size[0]}x{current_size[1]}', creative["id"])
            creatives.append({'id': creative["id"]})
    print('Creative ID #s are complete: ' + "[{0}]".format(', '.join(map(str, creatives))))
    return creatives

def drange(start, stop, step):
    # https://stackoverflow.com/questions/477486/how-to-use-a-decimal-range-step-value
    r = start
    while r < stop:
        yield r
        r += step

def get_pb_list(tier):
    pb = drange(tier["start"], tier["end"], tier["inc"])
    return ["%g" % x for x in pb]

def existing_keys(url, auth):
    return api_wrapper("get", url, auth)

def check_existence_key(new_key, existing_keys):
    for key in existing_keys["targeting-keys"]:
        if key["name"] == new_key:
            return True
        else:
            return False

def traffic_value(li_pb, value_url, auth, value_data):
    print('trafficking hb_pb values...')
    existing_keys_result = existing_keys(key_url, auth)
    for tier in li_pb: # grab each tier
        pb_list = get_pb_list(li_pb[tier])
        print(pb_list)
        for pb in pb_list:
            print(f'trafficking key & value: {pb}')
            pb = add_trailing_zero(pb)
            name = f'hb_pb_is_{pb}'
            key_existence = check_existence_key(name, existing_keys_result)
            if key_existence:
                error.push(f'Key Error: hb_pb is {pb}')
                print(f'Key Error: Duplicate key already exists "hb_pb_is_{pb}"')
                return
            key_send = key_data
            key_send["targeting-key"]["name"] = f'hb_pb_is_{pb}'
            key_send["targeting-key"]["type"] = 'numeric'
            response = api_wrapper("post", key_url, auth, key_send)
            if response is not False:
                key_id = response["targeting-key"]['id']
                value_send = value_data
                value_send["targeting-value"]["targeting_key_id"] = key_id
                value_send["targeting-value"]["name"] = f'{pb}'
                value_url_with_key = value_url + str(key_id)
                api_wrapper("post", value_url_with_key, auth, value_send)

def traffic_key(name, bidders, li_pb, key_url, auth, key_data):
    print('trafficking hb_bidder key...')
    key_send = key_data
    key_send["targeting-key"]["name"] = name
    existing_keys_result = existing_keys(key_url, auth)
    key_does_exist = check_existence_key("hb_bidder", existing_keys_result)
    if key_does_exist:
        new_key_name = input('Enter new targeting key name. hb_bidder is taken. NO spaces!')
        traffic_key(name_key_name, bidders, li_pb, key_url, auth, key_data)
    else:
        response = api_wrapper("post", key_url, auth, key_send)
        if response is not False:
            print(f'response key:', response)
            key_id = response["targeting-key"]['id']
            for bidder in bidders: # traffic key value targeting for bidders
                print('trafficking hb_bidder key values..')
                value_send = value_data
                value_send["targeting-value"]["targeting_key_id"] = key_id
                value_send["targeting-value"]["name"] = bidder
                value_url_with_key = value_url + str(key_id)
                api_wrapper("post", value_url_with_key, auth, value_send)

def traffic_campaigns(auth, campaign_url, campaign_data, li_pb):
    print('trafficking campaigns...')
    for tier in li_pb:
        camp_send = campaign_data

        camp_list = get_pb_list(li_pb[tier])

        for pb in camp_list:
            pb = add_trailing_zero(pb)
            #camp_send["campaign"]["name"] += str(li_pb[tier])
            camp_send["campaign"]["name"] = f'Pbjs_Campaign_hb_pb_is_{pb}'
            camp_send["campaign"]["line_item_id"] = pb_map["line_items"][pb]
            camp_send["campaign"]["profile_id"] = pb_map["profiles"][pb]
            camp_id = api_wrapper("post", campaign_url, auth, camp_send)
            if camp_id is not False:
                populate_map("campaigns", pb, camp_id["id"])

def traffic_li(auth, li_url, li_data, li_pb, creative_list):
    print('trafficking line items...')
    # populate total line items to be created
    for tier in li_pb: # each tier here.. tier_1 tier_2 tier_3
        li_send = li_data # grab line item template

        li_list = get_pb_list(li_pb[tier]) # list of our line items to create for this tier

        for pb in li_list:
            pb = add_trailing_zero(pb)
            li_send["line-item"]["revenue_value"] = pb
            li_send["line-item"]["name"] = f'Pbjs_LI_hb_pb_is_{pb}'
            li_send["line-item"]["creatives"] = creative_list
            li_id = api_wrapper("post", li_url, auth, li_send)
            if li_id is not False:
                populate_map("line_items", pb, li_id["id"])

def traffic_io(order_url, auth, order_data):
    print('trafficking insertion order...')
    # run traffic_io function and return IO id into li_data object
    io = api_wrapper("post", order_url, auth, order_data)
    if io is not False:
        populate_map("order", 1, io["id"])
        return io["id"]

def traffic_profile(auth, profile_url, profile_data, li_pb):
    print('trafficking profiles...')
    for tier in li_pb:
        profile_send = profile_data

        profile_list = get_pb_list(li_pb[tier])

        for pb in profile_list:
            pb = add_trailing_zero(pb)
            profile_send["profile"]["key_value_targets"]["kv_expression"]["exp"]["sbe"][1]["exp"]["key"] = f'hb_pb_is_{pb}'
            profile_send["profile"]["key_value_targets"]["kv_expression"]["exp"]["sbe"][1]["exp"]["vnm"] = int(round(float(f'{pb}'),2))
            profile = api_wrapper("post", profile_url, auth, profile_send)
            if profile is not False:
                populate_map("profiles", pb, profile["id"])


def traffic_apn():
    """
    This is a function that traffics line items into APN.
    """
    auth = {"Authorization":get_auth()}
    time.sleep(2)

    li_pb = load_tiers() # grab price buckets from config
    sizes = load_creative_sizes() # grab sizes from config


    io_id = traffic_io(order_url, auth, order_data)
    li_data["line-item"]["insertion_order_id"] = io_id

    time.sleep(2)

    traffic_key("hb_bidder", BIDDERS, li_pb, key_url, auth, key_data) # traffic key values. may not need to return ID#s
    traffic_value(li_pb, value_url, auth, value_data)
    time.sleep(5)

    creative_list = creatives(sizes, auth, creative_url, creative_data) # traffic and get our creative ID#s
    time.sleep(5)


    traffic_li(auth, li_url, li_data, li_pb, creative_list) # traffic line items
    time.sleep(5)

    traffic_profile(auth, profile_url, profile_data, li_pb)
    time.sleep(5)

    traffic_campaigns(auth, campaign_url, campaign_data, li_pb) # traffic campaigns
    time.sleep(5)

    print(f'Completed with {len(errors)} Errors: ', errors)
    print(f'Here are your APN assets: {pb_map}')
    time.sleep(3)


if __name__ == '__main__':
    traffic_apn()