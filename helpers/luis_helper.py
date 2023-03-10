# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from enum import Enum
from typing import Dict
from botbuilder.ai.luis import LuisRecognizer
from botbuilder.core import IntentScore, TopIntent, TurnContext

from booking_details import BookingDetails


class Intent(Enum):
    BOOK = "Book"
    INFO = "Info"
    NONE_INTENT = "None"


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
        Returns an object with preformatted LUIS results for the bot's dialogs to consume.
        """
        result = None
        intent = None

        try:
            recognizer_result = await luis_recognizer.recognize(turn_context)

            intent = recognizer_result.get_top_scoring_intent().intent

            if intent == Intent.BOOK.value or intent == Intent.INFO.value:
                result = BookingDetails()

                result.intent = intent

                # We need to get the result from the LUIS JSON which at every level returns an array.
                to_entities = recognizer_result.entities.get("$instance", {}).get(
                    "dst_city", []
                )
                if len(to_entities) > 0:
                    result.destination = to_entities[0]["text"].capitalize()
                    result.destination = result.destination.replace('.', '').strip()

                from_entities = recognizer_result.entities.get("$instance", {}).get(
                    "or_city", []
                )
                if len(from_entities) > 0:
                    result.origin = from_entities[0]["text"].capitalize()
                    result.origin = result.origin.replace('.', '').strip()

                budget_entities = recognizer_result.entities.get("$instance", {}).get(
                    "budget", []
                )
                if len(budget_entities) > 0:
                    result.budget = budget_entities[0]["text"].capitalize()
                    result.budget = result.budget.replace('.', '').strip()

                start_date_entities = recognizer_result.entities.get("$instance", {}).get(
                    "str_date", []
                )
                if len(start_date_entities) > 0:
                    result.start_travel_date = start_date_entities[0]["text"].capitalize()

                start_date_entities2 = recognizer_result.entities.get("datetime", [])

                if len(start_date_entities2) == 2:
                    result.start_travel_date = start_date_entities2[0]["timex"][0]

                end_date_entities = recognizer_result.entities.get("$instance", {}).get(
                    "end_date", []
                )
                if len(end_date_entities) > 0:
                    result.end_travel_date = end_date_entities[0]["text"].capitalize()

                end_date_entities2 = recognizer_result.entities.get("datetime", [])

                if len(end_date_entities2) == 2:
                    result.end_travel_date = end_date_entities2[1]["timex"][0]

        except Exception as exception:
            print(exception)

        return intent, result
