import os
import urllib.parse
import urllib.request
import base64
import json

from botbuilder.core import ActivityHandler, ConversationState, UserState, TurnContext
from botbuilder.schema import Activity, Attachment, AttachmentData
from botbuilder.dialogs import Dialog
from helpers.dialog_helper import DialogHelper

from purchase_details import PurchaseDetails

class DialogBot(ActivityHandler):
    def __init__(
        self,
        conversation_state: ConversationState,
        user_state: UserState,
        dialog: Dialog,
    ):
        if conversation_state is None:
            raise Exception(
                "[DialogBot]: Missing parameter. conversation_state is required"
            )
        if user_state is None:
            raise Exception("[DialogBot]: Missing parameter. user_state is required")
        if dialog is None:
            raise Exception("[DialogBot]: Missing parameter. dialog is required")

        self.conversation_state = conversation_state
        self.user_state = user_state
        self.dialog = dialog

    async def on_turn(self, turn_context: TurnContext):
        await super().on_turn(turn_context)

        # Save any state changes that might have occurred during the turn.
        await self.conversation_state.save_changes(turn_context, False)
        await self.user_state.save_changes(turn_context, False)

    async def on_message_activity(self, turn_context: TurnContext):
        if (turn_context.activity.attachments
            and len(turn_context.activity.attachments) > 0
        ):
            await self.handle_incoming_attachment(turn_context)
        else:
            await DialogHelper.run_dialog(
                self.dialog,
                turn_context,
                self.conversation_state.create_property("DialogState"),
            )

    async def handle_incoming_attachment(self, turn_context: TurnContext):
        """
        Handle attachments uploaded by users.
        The bot receives an Attachment in an Activity.
        The activity has a list of attachments.
        """
        for attachment in turn_context.activity.attachments:
            attachment_info = await self.download_attachment_and_write(attachment)
            if "filename" in attachment_info:

                ### classify this image, send a response ###
                path = attachment_info['local_path']
                purchase_details = PurchaseDetails()
                flower = purchase_details.classification(path)

                if flower is not None:
                    if flower[0] in ['a', 'e', 'i', 'o', 'u']:
                        prefix = 'an'
                    else:
                        prefix = 'a'
                    message_text = (
                        f"Got it - that looks like {prefix} {flower} to me."
                    )
                else:
                    message_text = (
                        f"Sorry, I am unable to classify a flower there."
                    )
                await turn_context.send_activity(message_text)

    async def download_attachment_and_write(self, attachment: Attachment) -> dict:
        """
        Retrieve the attachment via the attachments contentUrl.
        Returns a dictionary with keys "filename", "local_path".
        """
        try:
            response = urllib.request.urlopen(attachment.content_url)
            headers = response.info()

            # If user uploads JSON file, this prevents it from being written as
            # "{"type":"Buffer","data":[123,13,10,32,32,34,108..."
            if headers["content-type"] == "application/json":
                data = bytes(json.load(response)["data"])
            else:
                data = response.read()

            local_filename = os.path.join(os.getcwd(), attachment.name)
            with open(local_filename, "wb") as out_file:
                out_file.write(data)

            return {"filename": attachment.name, "local_path": local_filename}
        except Exception as exception:
            print(exception)
            return {}

