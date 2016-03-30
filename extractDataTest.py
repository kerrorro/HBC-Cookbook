from urllib.request import urlopen
from bs4 import BeautifulSoup
import re


class Recipe(object):
    def __init__(self):
        self.ingredientList = []


class TimeConverter(object):
    # Deletes the spaces in the string when initialized
    def __init__(self, raw_time):
        self.time = self.processSpaces(raw_time)

    def processSpaces(self, raw_time):
        self.time = raw_time.replace(" ", "")
        return self.time

    # Reports time in minutes by converting digits corresponding to hours. Functional if no hour digits are present.
    def toMin(self):
        digitHolder = ""
        minutes = 0
        for ch in self.time:
            if (re.match('[0-9]', ch) is not None):
                digitHolder = digitHolder + ch
            elif (ch.lower() == "h"):
                hours = float(digitHolder)
                minutes = hours * 60
                # Resets to capture minute digits
                digitHolder = ""
            elif (ch.lower() == "m"):
                if (digitHolder == ""):
                    digitHolder = 0
                minutes = minutes + float(digitHolder)
                break
            
        return (int(minutes))

    # Can add a toHour method, or other time converter methods if wanted.
    

# Extracts the integers out of a string.
def extractInt(string):
    digitHolder = ""
    # Extracts number of servings from the string servingsMatch
    for ch in string:
        if (re.match('[0-9]', ch) is not None):
            digitHolder = digitHolder + ch
    digits = int(digitHolder)
    return digits


def main():
    # Attempts to open url. If not accessible, prints error
    try:
        html = urlopen("http://allrecipes.com/recipe/236603/chef-johns-irish-stew/")
    except HTTPError as e:
        print(e)
    else:
        if html is None:
            print("URL is not found")
        else:
        
            bsObj = BeautifulSoup(html, "html.parser")

            # Obtains list of ingredients
            ingredientList = bsObj.findAll("span", {"itemprop":"ingredients"})
            for ingredient in ingredientList:
                print(ingredient.get_text())
            print()
            
            # Obtains times (make method that processes text (includes get_text))
            prepTime = bsObj.find("time", {"itemprop":"prepTime"}).get_text()
            cookTime = bsObj.find("time", {"itemprop":"cookTime"}).get_text()
            totalTime = bsObj.find("time", {"itemprop":"totalTime"}).get_text()
            print("Prep time:", prepTime,
                  "\nCook time:", cookTime,
                  "\nTotal time:", totalTime)
            print()

            """ EXAMPLE OF HOW TO USE TimeConverter object
    
            tcPrepTime = TimeConverter(prepTime)
            tcCookTime = TimeConverter(cookTime)
            tcTotalTime = TimeConverter(totalTime)
            print(tcPrepTime.toMin(), tcCookTime.toMin(), tcTotalTime.toMin())
            """

            # Obtains recipe name
            recipeName = bsObj.find("h1", {"class": "recipe-summary__h1", "itemprop": "name"}).get_text()
            print(recipeName)
            print()

            # Obtains calories
            calories = bsObj.find("span", {"class": "calorie-count"}).get_text()
            print(calories,
                  "\nExtracted calories integer:", extractInt(calories))
            print()

            # Obtains number of servings
            servingsMatch = bsObj.find(text = re.compile('yields [0-9]+ serving'))
            print(servingsMatch,
                  "\nExtracted servings integer:", extractInt(servingsMatch))
            print()
            
            # Obtains directions
            directions = bsObj.findAll("span", {"class":"recipe-directions__list--item"})
            for step in directions:
                print(step.get_text())
        
main()
