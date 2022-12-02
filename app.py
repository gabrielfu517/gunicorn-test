import os
import requests
import json
import shopify

from datetime import date
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from apscheduler.schedulers.background import BackgroundScheduler
from helpers import *



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


sched = BackgroundScheduler(daemon=True)
sched.add_job(sync_cron,'interval',minutes=1440)
sched.start()

# Configure application
app = Flask(__name__)

#scheduler.init_app(app)
#scheduler.start()
#app.run()