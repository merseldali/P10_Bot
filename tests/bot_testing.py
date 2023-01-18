import json

import aiounittest
from botbuilder.core import ConversationState, MemoryStorage, TurnContext
from botbuilder.core.adapters import TestAdapter
from botbuilder.dialogs import DialogSet, DialogTurnStatus
from botbuilder.dialogs.prompts import TextPrompt

from booking_details import BookingDetails  # type: ignore
from config import DefaultConfig  # type: ignore
from dialogs import BookingDialog, MainDialog  # type: ignore
from flight_booking_recognizer import FlightBookingRecognizer  # type: ignore
from helpers.luis_helper import Intent, LuisHelper  # type: ignore


class TestLuisHelper(aiounittest.AsyncTestCase):
    """Tests for the LUIS helper class"""

    async def test_execute_luis_query(self):
        """Tests the execute_luis_query method"""
        CONFIG = DefaultConfig()
        RECOGNIZER = FlightBookingRecognizer(CONFIG)

        async def exec_test(turn_context: TurnContext):
            """Executes the test"""
            # Call LUIS and gather any potential booking details. (Note the TurnContext has the response to the prompt.)
            intent, luis_result = await LuisHelper.execute_luis_query(
                RECOGNIZER, turn_context
            )
            await turn_context.send_activity(
                json.dumps(
                    {
                        "intent": intent,
                        "booking_details": luis_result.__dict__,
                    }
                )
            )

        adapter = TestAdapter(exec_test)

        await adapter.test(
            "Hello",
            json.dumps(
                {
                    "intent": Intent.INFO.value,
                    "booking_details": BookingDetails(
                        intent="Info",
                    ).__dict__,
                }
            ),
        )

        await adapter.test(
            "I want to go to London from Lyon.",
            json.dumps(
                {
                    "intent": Intent.BOOK.value,
                    "booking_details": BookingDetails(
                        origin="Lyon",
                        destination="London",
                        intent="Book",
                    ).__dict__,
                }
            ),
        )

        await adapter.test(
            "I want to leave on the 1st of September 2023 and to come back on the \
                20th of September 2023.",
            json.dumps(
                {
                    "intent": Intent.INFO.value,
                    "booking_details": BookingDetails(
                        start_travel_date="2023-09-01",
                        end_travel_date="2023-09-20",
                        intent="Info",
                    ).__dict__,
                }
            ),
        )

        await adapter.test(
            "I have a budget of $100.",
            json.dumps(
                {
                    "intent": Intent.INFO.value,
                    "booking_details": BookingDetails(
                        budget="$ 100",
                        intent="Info",
                    ).__dict__,
                }
            ),
        )


class MainDialogTest(aiounittest.AsyncTestCase):
    """Tests for the main dialog"""

    async def test_booking_dialog(self):
        """Tests the booking dialog"""

        async def exec_test(turn_context: TurnContext):
            """Executes the test"""
            dialog_context = await dialogs.create_context(turn_context)
            results = await dialog_context.continue_dialog()

            if results.status == DialogTurnStatus.Empty:
                await main_dialog.intro_step(dialog_context)

            elif results.status == DialogTurnStatus.Complete:
                await main_dialog.act_step(dialog_context)

            await conv_state.save_changes(turn_context)

        conv_state = ConversationState(MemoryStorage())
        dialogs_state = conv_state.create_property("dialog-state")
        dialogs = DialogSet(dialogs_state)
        booking_dialog = BookingDialog()
        main_dialog = MainDialog(
            FlightBookingRecognizer(DefaultConfig()), booking_dialog
        )
        dialogs.add(booking_dialog)

        text_prompt = await main_dialog.find_dialog(TextPrompt.__name__)
        dialogs.add(text_prompt)

        wf_dialog = await main_dialog.find_dialog("MainDialog")
        dialogs.add(wf_dialog)

        adapter = TestAdapter(exec_test)

        await adapter.test("Hi!", "What can I help you with today?")

        await adapter.test("Book a flight", "Where would you like to travel to? ✈")
        await adapter.test("Tokyo", "From what city will you be travelling? ✈")
        await adapter.test("Lyon", "▶ On what date would you like to travel? 🛫")
        await adapter.test(
            "1st of Septemberer 2023",
            "I'm sorry, for best results, please enter your travel date including the month, day and year.",
        )
        await adapter.test("2023-09-01", "◀ On what date would you like to travel back? 🛬")
        await adapter.test(
            "2023-09-20",
            "What is your budget in $? 💵",
        )
        await adapter.test(
            "500",
            "Please confirm, I have you traveling to: Tokyo from: Lyon on: 2023-09-01 to 2023-09-20 with a budget of "
            "500. (1) Yes or (2) No",
        )

    async def test_luis_dialog(self):
        """Tests the LUIS dialog"""

        async def exec_test(turn_context: TurnContext):
            """Executes the test"""
            dialog_context = await dialogs.create_context(turn_context)
            results = await dialog_context.continue_dialog()

            if results.status == DialogTurnStatus.Empty:
                await main_dialog.intro_step(dialog_context)

            elif results.status == DialogTurnStatus.Complete:
                await main_dialog.act_step(dialog_context)

            await conv_state.save_changes(turn_context)

        conv_state = ConversationState(MemoryStorage())
        dialogs_state = conv_state.create_property("dialog-state")
        dialogs = DialogSet(dialogs_state)
        booking_dialog = BookingDialog()
        main_dialog = MainDialog(
            FlightBookingRecognizer(DefaultConfig()), booking_dialog
        )
        dialogs.add(booking_dialog)

        text_prompt = await main_dialog.find_dialog(TextPrompt.__name__)
        dialogs.add(text_prompt)

        wf_dialog = await main_dialog.find_dialog("MainDialog")
        dialogs.add(wf_dialog)

        adapter = TestAdapter(exec_test)

        await adapter.test("Hi!", "What can I help you with today?")

        await adapter.test(
            "I want to book flight tickets from Lyon to Tokyo with a budget of 900. \
                I will leave on the 1st of September 2023 and will \
                    come back on the 20th of September 2023.",
            "Please confirm, I have you traveling to: Tokyo from: Lyon on: 2023-09-01 to 2023-09-20 with a budget of "
            "900. (1) Yes or (2) No"
        )
