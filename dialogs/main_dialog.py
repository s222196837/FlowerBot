from botbuilder.core import MessageFactory, TurnContext
from botbuilder.dialogs import ComponentDialog, DialogTurnResult
from botbuilder.dialogs import WaterfallStepContext, WaterfallDialog
from botbuilder.dialogs.prompts import TextPrompt, PromptOptions
from botbuilder.schema import InputHints

from purchase_details import PurchaseDetails
from flower_purchase_recognizer import FlowerPurchaseRecognizer
from helpers.luis_helper import LuisHelper, Intent
from .purchase_dialog import PurchaseDialog


class MainDialog(ComponentDialog):
    def __init__(
        self, luis_recognizer: FlowerPurchaseRecognizer, purchase_dialog: PurchaseDialog
    ):
        super(MainDialog, self).__init__(MainDialog.__name__)

        self._luis_recognizer = luis_recognizer
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
        if not self._luis_recognizer.is_configured:
            await step_context.context.send_activity(
                MessageFactory.text(
                    "NOTE: LUIS is not configured. To enable all capabilities, add 'LuisAppId', 'LuisAPIKey' and "
                    "'LuisAPIHostName' to the appsettings.json file.",
                    input_hint=InputHints.ignoring_input,
                )
            )

            return await step_context.next(None)
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
        if not self._luis_recognizer.is_configured:
            # LUIS is not configured.
            # run the PurchaseDialog path with an empty PurchaseDetailsInstance.
            return await step_context.begin_dialog(
                self._purchase_dialog_id, PurchaseDetails()
            )

        # Call LUIS and gather purchase details.
        intent, luis_result = await LuisHelper.execute_luis_query(
            self._luis_recognizer, step_context.context
        )

        if intent == Intent.PURCHASE_FLOWERS.value and luis_result:
            # Show a warning for item (flower) if we can't supply it.
            await MainDialog._show_warning_for_unsupported_flowers(
                step_context.context, luis_result
            )

            # Run the PurchaseDialog giving it whatever details we have from the LUIS call.
            return await step_context.begin_dialog(self._purchase_dialog_id, luis_result)

        # TODO: handle an image upload as well (here?)

        if intent == Intent.RECOMMEND_FLOWERS.value:
            # TODO: retrieve recommendations and display
            get_flowers_text = "Sit tight, getting recommendations"
            get_flowers_message = MessageFactory.text(
                get_flowers_text, get_flowers_text, InputHints.ignoring_input
            )
            await step_context.context.send_activity(get_flowers_message)

        else:
            didnt_understand_text = (
                "Sorry, I didn't get that. Please try asking in a different way"
            )
            didnt_understand_message = MessageFactory.text(
                didnt_understand_text, didnt_understand_text, InputHints.ignoring_input
            )
            await step_context.context.send_activity(didnt_understand_message)

        return await step_context.next(None)

    async def final_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        # If the child dialog ("PurchaseDialog") was cancelled or
        # the user failed to confirm, the result here will be null.

        if step_context.result is not None:
            result = step_context.result

            # Now we have all the purchase details, call the purchase service.

            # If the call to the purchase service was successful tell the user.
            msg_txt = f"Great, I've ordered some {result.item} flowers for you"
            message = MessageFactory.text(msg_txt, msg_txt, InputHints.ignoring_input)
            await step_context.context.send_activity(message)

        prompt_message = "What else can I do for you?"
        return await step_context.replace_dialog(self.id, prompt_message)

    @staticmethod
    async def _show_warning_for_unsupported_flowers(
        context: TurnContext, luis_result: PurchaseDetails
    ) -> None:
        if luis_result.unsupported_flowers:
            message_text = (
                f"Sorry but the following flowers are not available:"
                f" {', '.join(luis_result.unsupported_flowers)}"
            )
            message = MessageFactory.text(
                message_text, message_text, InputHints.ignoring_input
            )
            await context.send_activity(message)
