import importlib
from behave import *
from datetime import datetime as py_datetime
from nepalicalendar import NepDate

@given('core is loaded with gregorian calendar configuration')
def step_impl(context):
    core.datetime = importlib.import_module(
            '.datetimes.ad_datetime', 'core')

@given('core is loaded with nepali calendar configuration')
def step_impl(context):
    import core
    core.datetime = importlib.import_module(
            '.datetimes.ne_datetime', 'core')

@when('we request today')
def step_impl(context):
    import core
    context.response = core.datetime.date.today()

@then('we receive the gregorian today date')
def step_impl(context):
    # although py_datetime.today() provides a datetime, we want a date (without time part)
    assert(py_datetime.date(py_datetime.today()) == context.response)

@then('we receive the nepali today date')
def step_impl(context):    
    assert(NepDate.today() == context.response)    