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
    CLASSIFY_URL = "https://flowerbot-prediction.cognitiveservices.azure.com/"
    CLASSIFY_API_KEY = "76a6fbacaeb242818c613d1ee3bcb162"
    CLASSIFY_PROJECT = "82d55c80-b09c-4fb6-afe7-d4a0ed2686a3"
    CLASSIFY_ITERATION = "flowerbot-c78977fc-25b7-4eb0-9678-dbe5d7b65a7a"

    # Product recommendation services
    RECOMMEND_URL = "https://flowerbotyrpafrhf6sreews.azurewebsites.net/api/models/"
    RECOMMEND_MODEL = "4871529f-c9ac-4a1d-af27-70c58e6d2e71"
    RECOMMEND_API_KEY = "bmF1YXdhY3pyeXJjdw=="
