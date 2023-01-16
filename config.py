#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
from dotenv import load_dotenv

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    load_dotenv(override=True)

    PORT = 8000
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.getenv("MicrosoftAppPassword", "")
    LUIS_APP_ID = os.getenv("LuisAppId")
    LUIS_API_KEY = os.getenv("LuisAPIKey")
    # LUIS endpoint host name, ie "westus.api.cognitive.microsoft.com"
    LUIS_API_HOST_NAME = os.getenv("LuisAPIHostName")
    APPINSIGHTS_INSTRUMENTATION_KEY = os.getenv("AppInsightsInstrumentationKey")
