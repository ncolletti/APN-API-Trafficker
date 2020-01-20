from dotenv import load_dotenv
load_dotenv()

ADVERTISER_ID = os.getenv("ADV_ID")
PUB_NAME = os.getenv("PUB_NAME")
APN_BASE_URL = 'https://api.appnexus.com'
BIDDERS = os.getenv("BIDDERS")
PLACEMENT_TARGETS = os.getenv("PLACEMENT_TARGETS")

order_url = f'{APN_BASE_URL}/insertion-order?advertiser_id={ADVERTISER_ID}'
li_url = f'{APN_BASE_URL}/line-item?advertiser_id={ADVERTISER_ID}'
creative_url = f'{APN_BASE_URL}/creative?advertiser_id={ADVERTISER_ID}'
key_url = f'{APN_BASE_URL}/targeting-key'
value_url = f'{APN_BASE_URL}/targeting-value?targeting_key_id='
profile_url = f'{APN_BASE_URL}/profile?advertiser_id={ADVERTISER_ID}&member_id=1356'
campaign_url = f'{APN_BASE_URL}/campaign?advertiser_id={ADVERTISER_ID}'
category_url = f'{APN_BASE_URL}/content-cateogry'