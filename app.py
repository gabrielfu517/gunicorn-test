import os
import requests
import json
import shopify
import random
import string

from datetime import date
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from flask_apscheduler import APScheduler


# Configure application
app = Flask(__name__)

# Flask hook for cron job
scheduler = APScheduler()

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

def get_all_resources(resource):
    page_info = str()
    resources = list()
    while True:
        resources.extend(resource.find(limit=250, page_info=page_info))
        cursor = shopify.ShopifyResource.connection.response.headers.get('Link')
        if 'next' in cursor:
            page_info = cursor.split(';')[-2].strip('<>').split('page_info=')[1]
        else:
            break
    return resources


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str

@scheduler.task('interval', id='sync_wishlist_cron', seconds=86400)
def sync_cron():

    # Get customer list
    shop_url = "https://e9d82dadea8353e21e5788f4e3cfde61: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@barkmall.myshopify.com/admin"
    shopify.ShopifyResource.set_site(shop_url)
    shop = shopify.Shop.current

    customers = get_all_resources(shopify.Customer)

    # Push to dotdigital
    today = str(date.today())

    payload = []
    index = 0

    for customer in customers:

        index += 1

        if customer.email != None:

            # Get wishlist
            url = 'https://www.barkmall.com/apps/wishlist'

            params = dict(
                type='api',
                customerid=customer.id,
                version='1'
            )

            resp = requests.get(url=url, params=params)
            data = resp.json()

            new_data = {
                "key": "wishlist" + '-' + today + get_random_string(10),
                "contactIdentifier": customer.email,
                "json": data
            }
            payload.append(new_data)
            print(str(index) + '/' + str(len(customers)) + ' email - ' +customer.email)

    url = "https://r3-api.dotdigital.com/v2/contacts/transactional-data/import/shopify_wishlist"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Basic YXBpdXNlci03YzYzN2ZlZDBkMTFAYXBpY29ubmVjdG9yLmNvbToxR29AMTA3QENleE4="
    }

    print(payload)
    response = requests.post(url, json=payload, headers=headers)
    print(response.text)

scheduler.init_app(app)
scheduler.start()
app.run()