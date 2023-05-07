#!/bin/sh

# train a new recommender model
curl --json @train-recommender.json \
     --header "x-api-key: M3puanMydjdhc2p5eQ==" \
https://flowerbotyrpafrhf6sreews.azurewebsites.net/api/models

