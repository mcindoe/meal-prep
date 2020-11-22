* In writemeals(), check that the meals conform to some standards before writing
    - I.e. check that all ingredients are supported for example
    - Could also have a method of Meal which checks for all these things
* Ability to move around suggestions easily in looprecomend
    - Could offer move to or swap
    - And then use indexes to easily do this
* Check that additionals / extras / sides are compliant in checkdatafiles script
    - And that there are no unexpected keys in any meals dictionary
* Map units - currently some are measured in 'units' which says units in the message ...
* Need to sanity-check ingredients file: beans e.g. have sum = 202, some are measured in grams some in units
    - Wondering why some are measured in one and some in the other ...
    - Could use this ingredients measuredin to check meals.json is compliant

