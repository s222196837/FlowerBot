#!/bin/sh

SERVICE="flowerbotyrpafrhf6sreews"
APIKEY="bmF1YXdhY3pyeXJjdw=="
MODEL="4871529f-c9ac-4a1d-af27-70c58e6d2e71"
ITEM="P00001"

# test a recommendation

echo '{"itemId":"'$ITEM'"}' | \
curl --json @- \
     --header "x-api-key: $APIKEY" \
https://$SERVICE.azurewebsites.net/api/models/$MODEL/recommend

