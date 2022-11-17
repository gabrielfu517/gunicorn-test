import os
import requests
import random
import string
import shopify
from flask import redirect, render_template, request, session


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