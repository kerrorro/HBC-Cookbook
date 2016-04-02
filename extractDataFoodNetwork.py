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
        html = urlopen("http://www.foodnetwork.com/recipes/food-network-kitchens/roast-chicken-with-spring-vegetables-recipe.html")
    except HTTPError as e:
        print(e)
    else:
        if html is None:
            print("URL is not found")
        else:
        
            bsObj = BeautifulSoup(html, "html.parser")

            # Obtains list of ingredients
            ingredientList = bsObj.find("section", {"class":"ingredients-instructions recipe-instructions section"}).findAll("li", {"itemprop": "ingredients"})
                                  
            for ingredient in ingredientList:
                print(ingredient.get_text())
            print()

            
            # Obtains times
            cookingTimes = bsObj.find("div", {"class": "cooking-times"}).dl.children
            for time in cookingTimes:
                if (time.name == "dt"):
                    if ("total" in time.get_text().lower()):
                        totalTime = time.next_sibling.get_text()
                        print("Total Time:", totalTime)
                    elif ("prep" in time.get_text().lower()):
                        prepTime = time.next_sibling.get_text()
                        print ("Prep Time:", prepTime)
                    elif ("cook" in time.get_text().lower()):
                        cookTime = time.next_sibling.get_text()
                        print ("Cook Time:", cookTime)

            print()
            """ EXAMPLE OF HOW TO USE TimeConverter object
    
            tcPrepTime = TimeConverter(prepTime)
            tcCookTime = TimeConverter(cookTime)
            tcTotalTime = TimeConverter(totalTime)
            print(tcPrepTime.toMin(), tcCookTime.toMin(), tcTotalTime.toMin())
            """        

            # Obtains recipe name
            recipeName = bsObj.find("h1", {"itemprop": "name"}).get_text()
            print(recipeName)
            print()


            # Obtains number of servings
            servings = bsObj.find("div", {"class": "difficulty"}).dl.dd.get_text()
            servings = extractInt(servings)
            print("Servings:", servings)
            print()



            # Obtains directions
            directions = bsObj.find("div", {"itemprop":"recipeInstructions"}).findAll("p")
            for step in directions:
                print(step.get_text())
                
            print()



            # Obtains categories. Because the text is contained in a javascript function, regex is used to locate
            # the <li> and <a href> tags and isolate the category (key) and category value text. This data is then stored
            # in categoryDict. One category can have multiple values (saved in a list).
            raw_categories = bsObj.find("script", {"data-popover":"categories"}).get_text()
            raw_categories = raw_categories.splitlines()

            categoryDict = {}
            valueList = []
            for category in raw_categories:
                category = category.strip()
                if ("</li>" in category):
                    if ("</a>" not in category):
                        match = re.match("(^<li[\w =\"]*>)(.+)(</li>$)", category)
                        key = match.group(2)
                    else:
                        match = re.match("(^<li[\w =\"]*>)(<a href[\w =.\"/-]*>)(.+)(</a></li>$)", category)
                        value = match.group(3)
                        valueList.append(value)
                        # "last" ID represents the last value in that category (bc certain categories can have multiple values).
                        # In this case, resets value count
                        last = re.search("class=\"last\"" , category)
                        if (last):
                            categoryDict[key] = valueList
                            valueList = []
            print (categoryDict)
            print()
                        
                    

                         
                

            
            
        
main()
