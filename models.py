from constants import *


CREATIVE_TAG = """
<script>
 var w = window;
 for (i = 0; i < 10; i++) {
     w = w.parent;
     if (w.pbjs) {
         try {
             w.pbjs.renderAd(document, '#{HB_ADID}');
             break;
         } catch (e) {
             continue;
         }
     }
 }
</script>
"""

order_data = {
    "insertion-order": {
        "name": f'{PUB_NAME}_Pbjs_HB',
        "advertiser_id": ADVERTISER_ID
    }
}

li_data = {
    "line-item":{
        "name": "Pbjs hb_pb is ",  # set dynamically
        "advertiser_id": ADVERTISER_ID,
        "state": "active",
        "insertion_order_id": 0, # set dynamically
        "revenue_value": 0, # set dynamically
        "revenue_type": "cpm",
        "manage_creative": True,
        "creatives": [] # set dynamically
    }
}

creative_data = {
    "creative": {
        "name": "Pbjs HB", # set dynamically
        "advertiser_id": ADVERTISER_ID,
        "ad_type": "banner",
        "is_self_audited": True,
        "allow_audit": False,
        "width": 0, # set dynamically
        "height": 0, # set dynamically
        "content": CREATIVE_TAG,
        "template": {
            "id": 0 # set dynamically
        }
    }
}

key_data = {
    "targeting-key": {
        "name": "test", # set dynamically
        "type": "string"
    }
}

value_data = {
    "targeting-value": {
        "name": "test", # set dynamically
        "targeting_key_id": 0 # set dynamically
    }
}

campaign_data = {
    "campaign": {
        "state": "active",
        "name": "Pbjs Campaign hb_pb is ", # set dynamically
        "advertiser_id": ADVERTISER_ID,
        "line_item_id": 0, # set dynamically
        "inventory_type": "direct"
    }
}

category_data = {
    "content-category": {
        "name": "pbjs_hb",
        "description": "Any placements targeting this category will serve on Prebidjs HB LI."
    }
}

# setup one profile and populate each key value
profile_data = {
   "profile": {
       "inventory_action": "include",
       "advertiser_id": ADVERTISER_ID,
       "placement_targets": PLACEMENT_TARGETS, #PLACEMENT_TARGETS, # array/list of placements
        "key_value_targets": {
          "kv_expression": {
            "header": {
                "an_version": "1.0",
                "client_version": "1.0"
            },
            "exp": {
                "typ": "and",
                "sbe": [{
                    "exp": {
                        "typ": "in",
                        "key": "hb_bidder",
                        "vtp": "sta",
                        "vsa": ['appnexus', 'aol', 'rubicon', 'pulsepoint', 'sovrn', 'openx', 'sonobi', 'pubmatic']
                    }
                },
                {
                    "exp": {
                        "typ": "eq",
                        "key": "hb_pb is ", # 1.00 - set dynamically
                        "vtp": "num",
                        "vnm": 0 # set dynamically
                    }
                }
                ]
            }
            }
        }
    }
}