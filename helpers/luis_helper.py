from enum import Enum
from typing import Dict
from botbuilder.ai.luis import LuisRecognizer
from botbuilder.core import IntentScore, TopIntent, TurnContext

from purchase_details import PurchaseDetails


class Intent(Enum):
    PURCHASE_FLOWERS = "PurchaseFlowers"
    RECOMMEND_FLOWERS = "RecommendFlowers"
    CANCEL = "Cancel"
    NONE_INTENT = "NoneIntent"


def top_intent(intents: Dict[Intent, dict]) -> TopIntent:
    max_intent = Intent.NONE_INTENT
    max_value = 0.0

    for intent, value in intents:
        intent_score = IntentScore(value)
        if intent_score.score > max_value:
            max_intent, max_value = intent, intent_score.score

    return TopIntent(max_intent, max_value)


class LuisHelper:
    @staticmethod
    async def execute_luis_query(
        luis_recognizer: LuisRecognizer, turn_context: TurnContext
    ) -> (Intent, object):
        """
        Returns an object with preformatted LUIS results for Dialogs to consume.
        """
        result = None
        intent = None

        try:
            recognizer_result = await luis_recognizer.recognize(turn_context)

            intent = (
                sorted(
                    recognizer_result.intents,
                    key=recognizer_result.intents.get,
                    reverse=True,
                )[:1][0]
                if recognizer_result.intents
                else None
            )

            if intent in [
                Intent.PURCHASE_FLOWERS.value,
                Intent.RECOMMEND_FLOWERS.value
            ]:
                buynow = (intent == Intent.PURCHASE_FLOWERS.value)
                result = PurchaseDetails(buynow)

                # Get result from the LUIS JSON - every level returns an array.
                item_entities = recognizer_result.entities.get("$instance", {}).get(
                    "item", []
                )
                if len(item_entities) > 0:
                    if recognizer_result.entities.get("item", [{"$instance": {}}])[0][
                        "$instance"
                    ]:
                        result.item = item_entities[0]["text"].capitalize()
                    else:
                        result.unsupported_flowers.append(
                            item_entities[0]["text"].capitalize()
                        )

                user_entities = recognizer_result.entities.get("$instance", {}).get(
                    "user", []
                )
                if len(user_entities) > 0:
                    if recognizer_result.entities.get("user", [{"$instance": {}}])[0][
                        "$instance"
                    ]:
                        result.user = user_entities[0]["text"].capitalize()
                    else:
                        result.unsupported_flowers.append(
                            from_entities[0]["text"].capitalize()
                        )

        except Exception as exception:
            print(exception)

        return intent, result
