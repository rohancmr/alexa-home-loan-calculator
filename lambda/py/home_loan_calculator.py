# -*- coding: utf-8 -*-

import logging
import json

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model.ui import SimpleCard
from six import PY2


skill_name = "Indian Mobile Number Locator"
help_text = ("What is the 10 digit Indian mobile number that you "
             "want to check.")
goodbye_message = "Thank you for using Indian Mobile Number Locator. "\
                  "If you like this skill, please write your feedback "\
                  "on Amazon website. Goodbye!"


phone_number_slot_key = "PHONENUMBER"
phone_number_slot = "PhoneNumber"


sb = SkillBuilder()


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input):
    """Handler for Skill Launch."""
    # type: (HandlerInput) -> Response
    speech = "Welcome to Indian Mobile Number Locator. I can check the "\
             "operating circle and network carrier of an Indian mobile "\
             "number."

    handler_input.response_builder.speak(
        speech + " " + help_text).ask(help_text)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.HelpIntent"))
def help_intent_handler(handler_input):
    """Handler for Help Intent."""
    # type: (HandlerInput) -> Response
    handler_input.response_builder.speak(help_text).ask(help_text)
    return handler_input.response_builder.response


@sb.request_handler(
    can_handle_func=lambda handler_input:
        is_intent_name("AMAZON.CancelIntent")(handler_input) or
        is_intent_name("AMAZON.StopIntent")(handler_input))
def cancel_and_stop_intent_handler(handler_input):
    """Single handler for Cancel and Stop Intent."""
    # type: (HandlerInput) -> Response
    speech_text = goodbye_message

    return handler_input.response_builder.speak(speech_text).response


@sb.request_handler(can_handle_func=is_request_type("SessionEndedRequest"))
def session_ended_request_handler(handler_input):
    """Handler for Session End."""
    # type: (HandlerInput) -> Response
    return handler_input.response_builder.response


def _check_phone_number(PhoneNumber):
    """
    """
    try:
        with open('telecom_circle.json', 'r') as tc:
            circle_code = json.load(tc)
        with open('carrier_code.json', 'r') as cc:
            carrier_code = json.load(cc)
        with open('phone_number_carrier_circle.json', 'r') as pncc:
            pno_carrier_circle = json.load(pncc)

        phno_length = len(PhoneNumber)
        if phno_length < 4:
            message = "An Indian mobile number cannot have {} digit. "\
                      "Please check the number.".format(str(phno_length))
        else:
            msc_code = PhoneNumber[0:4]

            value = pno_carrier_circle[msc_code]
            try:
                carrier = carrier_code[value["network"]]
            except KeyError:
                carrier = None
            try:
                circle = circle_code[value["circle"]]
            except KeyError:
                circle = None
            pn_split = " ".join(list(PhoneNumber))
            if circle is not None and carrier is not None and \
                    phno_length != 10:
                message = "Phone number {} does not have 10 "\
                          "digits but "\
                          "based on first four digits it "\
                          "belongs to {} circle of {}....{}"\
                          .format(pn_split, circle, carrier,
                                  goodbye_message)
            elif circle is not None and carrier is not None and \
                    phno_length == 10:
                message = "Phone number {} belongs to {} circle "\
                          "of {}...{}"\
                          .format(pn_split, circle, carrier,
                                  goodbye_message)
            elif circle is None and carrier is not None and \
                    phno_length != 10:
                message = "Phone number {} does not have 10 "\
                          "digits but "\
                          "based on first four digits it "\
                          "belongs to {}....{}"\
                          .format(pn_split, carrier, goodbye_message)
            elif circle is not None and carrier is None and \
                    phno_length != 10:
                message = "Phone number {} does not have 10 "\
                          "digits but "\
                          "based on first four digits it "\
                          "belongs to {} circle....{}"\
                          .format(pn_split, circle, goodbye_message)
            elif circle is None and carrier is not None and \
                    phno_length == 10:
                message = "Phone number {} "\
                          "belongs to {}....{}"\
                          .format(pn_split, carrier, goodbye_message)
            elif circle is not None and carrier is None and \
                    phno_length == 10:
                message = "Phone number {} "\
                          "belongs to {} circle....{}"\
                          .format(pn_split, circle, goodbye_message)
            else:
                message = "Sorry !! No record found for mobile number "\
                          "{}.......{}".format(pn_split, goodbye_message)
    except Exception as exc:
        message = None

    return message


@sb.request_handler(can_handle_func=is_intent_name("LocatePhoneNumberIntent"))
def locate_phone_number_handler(handler_input):
    """Check if phone number is provided in slot values. If provided, then
    locate the number.
    If not, then it asks user to provide the phone number.
    """
    # type: (HandlerInput) -> Response
    slots = handler_input.request_envelope.request.intent.slots

    if phone_number_slot in slots:
        PhoneNumber = slots[phone_number_slot].value
        speech = _check_phone_number(PhoneNumber)
    else:
        speech = help_text

    handler_input.response_builder.speak(speech)
    return handler_input.response_builder.response


@sb.request_handler(can_handle_func=is_intent_name("AMAZON.FallbackIntent"))
def fallback_handler(handler_input):
    """AMAZON.FallbackIntent is only available in en-US locale.
    This handler will not be triggered except in that locale,
    so it is safe to deploy on any locale.
    """
    # type: (HandlerInput) -> Response
    speech = (
        "The {} can't help you with that.  "
        "I can check the operating circle and network carrier of an Indian "
        "mobile number. {}").format(skill_name, help_text)
    reprompt = ("You can tell me to check operating "
                "circle and network carrier of an Indian mobile number "
                "by saying, check followed by 10 digit mobile number.")
    handler_input.response_builder.speak(speech).ask(reprompt)
    return handler_input.response_builder.response


def convert_speech_to_text(ssml_speech):
    """convert ssml speech to text, by removing html tags."""
    # type: (str) -> str
    s = SSMLStripper()
    s.feed(ssml_speech)
    return s.get_data()


@sb.global_response_interceptor()
def add_card(handler_input, response):
    """Add a card by translating ssml text to card content."""
    # type: (HandlerInput, Response) -> None
    response.card = SimpleCard(
        title=skill_name,
        content=convert_speech_to_text(response.output_speech.ssml))


@sb.global_response_interceptor()
def log_response(handler_input, response):
    """Log response from alexa service."""
    # type: (HandlerInput, Response) -> None
    print("Alexa Response: {}\n".format(response))


@sb.global_request_interceptor()
def log_request(handler_input):
    """Log request to alexa service."""
    # type: (HandlerInput) -> None
    print("Alexa Request: {}\n".format(handler_input.request_envelope.request))


@sb.exception_handler(can_handle_func=lambda i, e: True)
def all_exception_handler(handler_input, exception):
    """Catch all exception handler, log exception and
    respond with custom message.
    """
    # type: (HandlerInput, Exception) -> None
    print("Encountered following exception: {}".format(exception))

    speech = "Sorry, there was some problem. Please try again!!"
    handler_input.response_builder.speak(speech).ask(speech)

    return handler_input.response_builder.response


# Convert SSML to Card text ############
# This is for automatic conversion of ssml to text content on simple card
# You can create your own simple cards for each response, if this is not
# what you want to use.


try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser


class SSMLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.full_str_list = []
        if not PY2:
            self.strict = False
            self.convert_charrefs = True

    def handle_data(self, d):
        self.full_str_list.append(d)

    def get_data(self):
        return ''.join(self.full_str_list)

################################################


# Handler to be provided in lambda console.
lambda_handler = sb.lambda_handler()
