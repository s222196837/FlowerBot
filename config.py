#!/usr/bin/env python3

import os

class DefaultConfig:
    """ Bot Configuration """
    PORT = 3978
    APP_ID = "" #"FlowerBot"
    APP_PASSWORD = ""

    # Application defaults
    MAX_USERS = 64
    BEST_FLOWER = 'sunflower'

    # Image classification services
    CLASSIFY_URL = "https://flowerbot002-prediction.cognitiveservices.azure.com/"
    CLASSIFY_API_KEY = "395816cd19174d6a91be4ee588053fee"
    CLASSIFY_PROJECT = "5478e771-8f36-4b82-a455-9bc728158288"
    CLASSIFY_ITERATION = "flowerbot-8be0259d-9193-4fb5-a902-10ef62840711"

    # Product recommendation services
    RECOMMEND_URL = "https://flowerbotyrpafrhf6sreews.azurewebsites.net/api/models/"
    RECOMMEND_MODEL = "ebd580dc-6954-4fe0-ac13-fdc45bb22f88"
    RECOMMEND_API_KEY = "YWs2NXp1ZTRqaXh3aQ=="
