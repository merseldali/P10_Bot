# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from datatypes_date_time.timex import Timex

from botbuilder.dialogs import WaterfallDialog, WaterfallStepContext, DialogTurnResult
from botbuilder.dialogs.prompts import ConfirmPrompt, TextPrompt, PromptOptions
from botbuilder.core import BotTelemetryClient, MessageFactory, NullTelemetryClient
from botbuilder.core.bot_telemetry_client import Severity
from botbuilder.schema import InputHints
from .cancel_and_help_dialog import CancelAndHelpDialog
from .date_resolver_dialog import DateResolverDialog


class BookingDialog(CancelAndHelpDialog):
    def __init__(self, dialog_id: str = None, telemetry_client: BotTelemetryClient = NullTelemetryClient()):
        super(BookingDialog, self).__init__(dialog_id or BookingDialog.__name__)
        self.telemetry_client = telemetry_client

        textprompt = TextPrompt(TextPrompt.__name__)
        textprompt.telemetry_client = telemetry_client
        self.add_dialog(textprompt)

        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(DateResolverDialog("StartDate", self.telemetry_client))
        self.add_dialog(DateResolverDialog("EndDate", self.telemetry_client))

        wfdialog = WaterfallDialog(
            WaterfallDialog.__name__,
            [
                self.destination_step,
                self.origin_step,
                self.start_travel_date_step,
                self.end_travel_date_step,
                self.budget_step,
                self.confirm_step,
                self.final_step,
            ],
        )
        wfdialog.telemetry_client = telemetry_client
        self.add_dialog(wfdialog)

        self.initial_dialog_id = WaterfallDialog.__name__

    async def destination_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        If a destination city has not been provided, prompt for one.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options

        if booking_details.destination is None:
            message_text = "Where would you like to travel to? ✈"
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        return await step_context.next(booking_details.destination)

    async def origin_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        """
        If an origin city has not been provided, prompt for one.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options

        # Capture the response to the previous step's prompt
        booking_details.destination = step_context.result
        if booking_details.origin is None:
            message_text = "From what city will you be travelling? ✈"
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )
        return await step_context.next(booking_details.origin)

    async def start_travel_date_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        If a travel date has not been provided, prompt for one.
        This will use the DATE_RESOLVER_DIALOG.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.origin = step_context.result
        if not booking_details.start_travel_date or self.is_ambiguous(
            booking_details.start_travel_date
        ):
            return await step_context.begin_dialog(
                "StartDate", booking_details.start_travel_date
            )
        return await step_context.next(booking_details.start_travel_date)

    async def end_travel_date_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        If a travel date has not been provided, prompt for one.
        This will use the DATE_RESOLVER_DIALOG.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.start_travel_date = step_context.result
        if not booking_details.end_travel_date or self.is_ambiguous(
            booking_details.end_travel_date
        ):
            return await step_context.begin_dialog(
                "EndDate", booking_details.end_travel_date
            )
        return await step_context.next(booking_details.end_travel_date)

    async def budget_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """Prompt for travel budget."""
        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.end_travel_date = step_context.result

        if booking_details.budget is None:
            message_text = "What is your budget in $? 💵"
            prompt_message = MessageFactory.text(
                message_text, message_text, InputHints.expecting_input
            )
            return await step_context.prompt(
                TextPrompt.__name__, PromptOptions(prompt=prompt_message)
            )

        return await step_context.next(booking_details.budget)

    async def confirm_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        """
        Confirm the information the user has provided.
        :param step_context:
        :return DialogTurnResult:
        """
        booking_details = step_context.options

        # Capture the results of the previous step
        booking_details.budget = step_context.result
        message_text = (
            f"Please confirm, I have you traveling to: { booking_details.destination } from: "
            f"{ booking_details.origin } on: { booking_details.start_travel_date} to "
            f"{ booking_details.end_travel_date } with a budget of { booking_details.budget }."
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

        booking_details = step_context.options

        if step_context.result:
            self.telemetry_client.track_trace(
                "booking_success",
                properties=booking_details.__dict__,
            )

            return await step_context.end_dialog(booking_details)

        self.telemetry_client.track_trace(
            "booking_rejected",
            severity=Severity.warning,
            properties=booking_details.__dict__,
        )

        return await step_context.end_dialog()

    def is_ambiguous(self, timex: str) -> bool:
        timex_property = Timex(timex)
        return "definite" not in timex_property.types
