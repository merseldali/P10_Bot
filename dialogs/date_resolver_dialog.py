# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from datatypes_date_time.timex import Timex

from botbuilder.core import BotTelemetryClient, MessageFactory, NullTelemetryClient
from botbuilder.dialogs import WaterfallDialog, DialogTurnResult, WaterfallStepContext
from botbuilder.dialogs.prompts import (
    DateTimePrompt,
    PromptValidatorContext,
    PromptOptions,
    DateTimeResolution,
)
from botbuilder.schema import InputHints
from .cancel_and_help_dialog import CancelAndHelpDialog


class DateResolverDialog(CancelAndHelpDialog):
    def __init__(self, dialog_id: str = None, telemetry_client: BotTelemetryClient = NullTelemetryClient()):
        super(DateResolverDialog, self).__init__(
            dialog_id or DateResolverDialog.__name__
        )
        self._dialog_id = dialog_id
        self.telemetry_client = telemetry_client

        dateprompt = DateTimePrompt(DateTimePrompt.__name__, DateResolverDialog.datetime_prompt_validator)
        dateprompt.telemetry_client = telemetry_client
        self.add_dialog(dateprompt)

        wfdialog = WaterfallDialog(
            WaterfallDialog.__name__ + "2", [self.initial_step, self.final_step]
        )
        wfdialog.telemetry_client = telemetry_client
        self.add_dialog(wfdialog)

        self.initial_dialog_id = WaterfallDialog.__name__ + "2"

    async def initial_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        timex = step_context.options

        if self._dialog_id == "StartDate":
            prompt_msg_text = "▶ On what date would you like to travel? 🛫"
            reprompt_msg_text = "I'm sorry, for best results, please enter your travel date including the month, " \
                                "day and year. "
        else:
            prompt_msg_text = "◀ On what date would you like to travel back? 🛬"
            reprompt_msg_text = "I'm sorry, for best results, please enter your return travel date including the " \
                                "month, day and year. "

        prompt_msg = MessageFactory.text(
            prompt_msg_text, prompt_msg_text, InputHints.expecting_input
        )

        reprompt_msg = MessageFactory.text(
            reprompt_msg_text, reprompt_msg_text, InputHints.expecting_input
        )

        if timex is None:
            # We were not given any date at all so prompt the user.
            return await step_context.prompt(
                DateTimePrompt.__name__,
                PromptOptions(prompt=prompt_msg, retry_prompt=reprompt_msg),
            )
        # We have a Date we just need to check it is unambiguous.
        if "definite" not in Timex(timex).types:
            # This is essentially a "reprompt" of the data we were given up front.
            return await step_context.prompt(
                DateTimePrompt.__name__, PromptOptions(prompt=reprompt_msg)
            )

        return await step_context.next(DateTimeResolution(timex=timex))

    async def final_step(self, step_context: WaterfallStepContext):
        timex = step_context.result[0].timex
        return await step_context.end_dialog(timex)

    @staticmethod
    async def datetime_prompt_validator(prompt_context: PromptValidatorContext) -> bool:
        if prompt_context.recognized.succeeded:
            timex = prompt_context.recognized.value[0].timex.split("T")[0]

            # TODO: Needs TimexProperty
            return "definite" in Timex(timex).types

        return False
