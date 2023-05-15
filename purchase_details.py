from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
from msrest.authentication import ApiKeyCredentials

from urllib import parse, request
import pandas as pd
import random
import time
import json
import os

from config import DefaultConfig

CONFIG = DefaultConfig()

class PurchaseDetails:
    def __init__(
        self,
        transact: bool = True,
        user: str = None,
        item: str = None,
        datetime: str = None,
        unsupported_flowers = None,
    ):
        self.purchase = transact # alternative is to recommend, not buy

        # pick a random ID as there is no account management (nor shop)
        total_users = CONFIG.MAX_USERS
        if user is None:
            user = random.randint(1, total_users)
        self.user = user
        self.item = item

        if datetime is None:
            datetime = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime())
        self.datetime = datetime

        if unsupported_flowers is None:
            unsupported_flowers = ['dandelion'] # weed
        self.unsupported_flowers = unsupported_flowers

        self.load_catalog()

    def load_catalog(self):
        """ get plant identifiers from the catalog, returns dictionary """
        flowers = 'data/flowers.catalog'
        columns = ['item', 'name', 'group']
        catalog = pd.read_csv(flowers, header=None, names=columns)
        catalog = pd.DataFrame(catalog, columns=['item', 'name'])
        inverse = dict([(i,n) for n, i in zip(catalog.name, catalog.item)])
        catalog = dict([(n,i) for n, i in zip(catalog.name, catalog.item)])
        self.supported_flowers = catalog
        self.supported_items = inverse  # reverse lookup

    def item_catalog(self, flower):
        """ lookup a flower in the catalog dictionary, returns item ID """
        if flower not in self.supported_flowers:
            return None
        return self.supported_flowers[flower]

    def flower_catalog(self, item):
        """ lookup an item in the catalog dictionary, returns flower """
        if item not in self.supported_items:
            return None
        return self.supported_items[item]

    def set_item(self, flower):
        """ set item to canonical name: lowercase, no spaces, singular """
        flower = flower.lower()
        flower = flower.replace(' ', '_')
        flower = flower.replace('  ', '_')
        flower = flower.rstrip("_")
        if flower in self.supported_flowers:
            self.item = flower
        else:
            self.item = None

    def set_user(self, identity):
        """ set user to ID - when numeric convert into U-prefixed form """
        if isinstance(identity, int):
            self.user = 'U' + str(identity).zfill(5)
        else:
            self.user = identity


    def fetch_recommendations(self, itemid):
        """ fetch recommendation result dict (item-to-item) """
  
        url = CONFIG.RECOMMEND_URL + CONFIG.RECOMMEND_MODEL + '/recommend'
        post = { 'itemId': itemid }
        data = parse.urlencode(post).encode()

        req = request.Request(url, data=data) # data makes a "POST"
        req.add_header('Content-Type', 'application/json')
        req.add_header('x-api-key', CONFIG.RECOMMEND_API_KEY)

        try:
            response = request.urlopen(req)
            respbody = response.read()
            respjson = json.loads(respbody.decode("utf-8"))
            return respjson

        except: # recommender endpoint unavailable
            pass
        return []


    def recommendation(self, item):
        """ query endpoint for top recommendation (item-to-item) """
        if item is None:
            item = CONFIG.BEST_FLOWER
        item_id = self.item_catalog(item)

        # talk to the endpoint
        recommendations = self.fetch_recommendations(item_id)

        # unpack the result and find the top recommendation
        max_score = 0.0
        for recommendation in recommendations:
            score = recommendation['score']
            if score >= max_score:
                max_score = score
                item_id = recommendation['recommendedItemId'].upper()

        result = self.flower_catalog(item_id)
        #print('Recommending:', item_id, result)
        return result


    def fetch_classifications(self, path):
        """ fetch classification result dict (image-to-tag) """

        cs = ApiKeyCredentials(in_headers={"Prediction-key": CONFIG.CLASSIFY_API_KEY})
        predictor = CustomVisionPredictionClient(CONFIG.CLASSIFY_URL, cs)

        try:
            with open(path, mode="rb") as image:
                return predictor.detect_image(CONFIG.CLASSIFY_PROJECT, CONFIG.CLASSIFY_ITERATION, image)
        except: # classification endpoint unavailable
            pass
        return []

    def classification(self, path):
        """ query endpoint for top classification (image-to-tag) """
       
        print('Classifying image:', path)
        classifications = self.fetch_classifications(path)

        # unpack the result and find the top classification
        item_tag = None
        max_score = 0.0
        for prediction in classifications.predictions:
            score = prediction.probability
            if score >= max_score:
                max_score = score
                item_tag = prediction.tag_name

        #print('Classified image:', item_tag)
        return item_tag
