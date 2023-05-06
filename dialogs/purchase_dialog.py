from botbuilder.dialogs import DialogTurnResult
from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions
from botbuilder.core import MessageFactory
from botbuilder.schema import InputHints

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

        #if purchase_details.transact is False:
            ### TODO: make a recommendation

        if purchase_details.item is None:
            message_text = "What sort of flowers are you looking for?"
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        return await step_context.next(purchase_details.item)

    async def confirm_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        Confirm the information the user has provided.
        :param step_context:
        :return DialogTurnResult:
        """
        purchase_details = step_context.options

        # Capture the results of the previous step
        purchase_details.item = step_context.result
        message_text = (
            f"Please confirm, you want to purchase some { purchase_details.item }?"
        )
        prompt_message = MessageFactory.text(
            message_text, message_text, InputHints.expecting_input
        )

        # Offer a YES/NO prompt.
        return await step_context.prompt(
            ConfirmPrompt.__name__, PromptOptions(prompt=prompt_message)
        )

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        Complete the interaction and end the dialog.
        :param step_context:
        :return DialogTurnResult:
        """
        if step_context.result:
            purchase_details = step_context.options

            return await step_context.end_dialog(purchase_details)
        return await step_context.end_dialog()
