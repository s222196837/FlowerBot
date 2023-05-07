import os
import json

from botbuilder.core import MessageFactory, TurnContext
from botbuilder.dialogs import ComponentDialog, DialogTurnResult
from botbuilder.dialogs import WaterfallStepContext, WaterfallDialog
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.schema import Attachment, InputHints

from purchase_details import PurchaseDetails
from .purchase_dialog import PurchaseDialog


class MainDialog(ComponentDialog):
    def __init__(
        self, purchase_dialog: PurchaseDialog
    ):
        super(MainDialog, self).__init__(MainDialog.__name__)

        self._purchase_dialog_id = purchase_dialog.id

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(purchase_dialog)
        self.add_dialog(
            WaterfallDialog(
                "WFDialog", [self.intro_step, self.act_step, self.final_step]
            )
        )

        self.initial_dialog_id = "WFDialog"

    async def intro_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        message_text = (
            str(step_context.options)
            if step_context.options
            else "What can I help you with today?"
        )
        prompt_message = MessageFactory.text(
            message_text, message_text, InputHints.expecting_input
        )

        return await step_context.prompt(
            TextPrompt.__name__, PromptOptions(prompt=prompt_message)
        )

    async def act_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        # run the PurchaseDialog path with an empty PurchaseDetailsInstance.
        return await step_context.begin_dialog(
            self._purchase_dialog_id, PurchaseDetails()
        )

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        # If the child dialog ("PurchaseDialog") was cancelled or
        # the user failed to confirm, the result here will be null.

        if step_context.result is not None:
            result = step_context.result

            # Now we have all the purchase details, call the purchase service.

            # If the call to the purchase service was successful tell the user.
            delivery_card = self.create_adaptive_card_attachment()
            delivery_text = f"Great, I've ordered a {result.item} plant for you!"
            delivery_message = MessageFactory.attachment(
                delivery_card, delivery_text, InputHints.ignoring_input
            )
            await step_context.context.send_activity(delivery_message)

        prompt_message = "What else can I do for you?"
        return await step_context.replace_dialog(self.id, prompt_message)

    @staticmethod
    def create_adaptive_card_attachment():
        """ Load attachment from file """
        relative_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(relative_path, "../cards/deliveryCard.json")
        with open(path) as in_file:
            card = json.load(in_file)

        return Attachment(
            content_type="application/vnd.microsoft.card.adaptive", content=card
        )
