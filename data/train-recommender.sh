#!/bin/sh

# train a new recommender model
curl --json @train-recommender.json \
     --header "x-api-key: dTRyZWxid29ia2Z0aQ==" \
https://flowerbotyrpafrhf6sreews.azurewebsites.net/api/models

