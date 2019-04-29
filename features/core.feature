Feature: calendars

    Scenario: gregorian calendar today
        Given core is loaded with gregorian calendar configuration
         When we request today
         Then we receive the gregorian today date

    Scenario: nepali calendar today
        Given core is loaded with nepali calendar configuration
         When we request today
         Then we receive the nepali today date         