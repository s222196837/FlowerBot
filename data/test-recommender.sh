#!/bin/sh

SERVICE="flowerbotyrpafrhf6sreews"
APIKEY="YWs2NXp1ZTRqaXh3aQ=="
MODEL="ebd580dc-6954-4fe0-ac13-fdc45bb22f88"
ITEM="P00013"

# test a recommendation

echo '{"itemId":"'$ITEM'"}' | \
curl --json @- \
     --header "x-api-key: $APIKEY" \
https://$SERVICE.azurewebsites.net/api/models/$MODEL/recommend

