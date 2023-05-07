import os
import json

from botbuilder.dialogs import DialogTurnResult
from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions
from botbuilder.core import MessageFactory
from botbuilder.schema import Attachment, InputHints

from purchase_details import PurchaseDetails
from .cancel_and_help_dialog import CancelAndHelpDialog
from .cancel_and_help_dialog import CancelAndHelpDialog


class PurchaseDialog(CancelAndHelpDialog):
    def __init__(self, dialog_id: str = None):
        super(PurchaseDialog, self).__init__(dialog_id or PurchaseDialog.__name__)

        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.flowers_step,
                    self.picture_step,
                    self.confirm_step,
                    self.final_step,
                ],
            )
        )

        self.initial_dialog_id = WaterfallDialog.__name__

    async def flowers_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        If a flower (item) has not been provided, prompt for one.
        :param step_context:
        :return DialogTurnResult:
        """
        purchase_details = step_context.options

        if purchase_details.item is None:
            message_text = "What sort of flowers are you looking for?"
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        return await step_context.next(purchase_details.item)

    async def picture_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        Present the information the user will choose.
        :param step_context:
        :return DialogTurnResult:
        """
        purchase_details = step_context.options

        # Capture the results of the previous step
        purchase_details.set_item(step_context.result)

        # If nothing was found or requested to do so, make a recommendation
        if purchase_details.purchase == False:

            recommendation = purchase_details.recommendation(purchase_details.item)
            purchase_details.set_item(recommendation)
            message_text = (
                f"Would you like to buy a { purchase_details.item } plant?"
            )

        elif purchase_details.item == None:

            recommendation = purchase_details.recommendation(None)
            purchase_details.set_item(recommendation)
            message_text = (
                f"My catalog is limited, would you like a { purchase_details.item } plant instead?"
            )

        else:
            message_text = (
                f"I've got { purchase_details.item } plants like this - is this right?"
            )

        # Send an adaptive card with the plant image first
        picture_card = self.create_adaptive_card_attachment(purchase_details.item)
        picture_message = MessageFactory.attachment(
            picture_card, message_text, InputHints.expecting_input
        )

        # Check we're on the right path before proceeding to purchase.
        return await step_context.prompt(
            ConfirmPrompt.__name__, PromptOptions(prompt=picture_message)
        )

    async def confirm_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        Confirm the information the user has provided.
        :param step_context:
        :return DialogTurnResult:
        """
        if step_context.result:
            purchase_details = step_context.options

            message_text = (
                f"Please confirm you want to buy a { purchase_details.item } plant?"
            )
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
    
            # Offer a final YES/NO prompt before proceeding with purchase.
            return await step_context.prompt(
                ConfirmPrompt.__name__, PromptOptions(prompt=prompt_message)
            )

        return await step_context.end_dialog()

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        Complete the interaction and end the dialog.
        :param step_context:
        :return DialogTurnResult:
        """
        if step_context.result:
            purchase_details = step_context.options
            ## In a real shop update the transation record here ##
            return await step_context.end_dialog(purchase_details)

        return await step_context.end_dialog()

    @staticmethod
    def create_adaptive_card_attachment(plant):
        """ Load attachment from file """
        relative_path = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(relative_path, "../cards/" + plant + "Card.json")
        with open(path) as in_file:
            card = json.load(in_file)

        return Attachment(
            content_type="application/vnd.microsoft.card.adaptive", content=card
        )

