# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.


class BookingDetails:
    def __init__(
        self,
        destination: str = None,
        origin: str = None,
        start_travel_date: str = None,
        end_travel_date: str = None,
        budget: str = None,
        intent: str = None,
    ):
        self.destination = destination
        self.origin = origin
        self.start_travel_date = start_travel_date
        self.end_travel_date = end_travel_date
        self.budget = budget
        self.intent = intent
