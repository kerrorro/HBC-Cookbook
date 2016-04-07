"""
Created by Caroline Chen on 4/1/16
Last Updated: 4/5/16
Description:
            This webcrawler finds and crawls through recipe articles from foodnetwork.com by using BeautifulSoup
            to search a page for all hrefs and within those hrefs to determine whether the link is actually a recipe.
            It will be used to populate a recipe box database with the desired number of recipes by parsing ingredients,
            cooking times, servings, level, directions, and recipe title.

"""             

from bs4 import BeautifulSoup
from bs4 import Comment
from urllib.request import urlopen
import random
import re


def convertToMin(raw_time):
    time = raw_time.replace(" ", "")
    # Reports time in minutes by converting digits corresponding to hours. Functional if no hour digits are present.
    digitHolder = ""
    minutes = 0
    for ch in time:
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
            
    return int(minutes)
    

def extractIngredients(bsObj):
    try:
        # Obtains list of ingredients
        ingredientList = bsObj.find("section", {"class":"ingredients-instructions recipe-instructions section"}).findAll("li", {"itemprop": "ingredients"})
        ingredientText = []
        for ingredient in ingredientList:
            print(ingredient.get_text())
            ingredientText.append(ingredient.get_text())
        return {"INGREDIENTS":ingredientText}
    except AttributeError:
        print ("Could not parse ingredients")
        pass
    finally:
        print()
        print()

def extractCookingTimes(bsObj):
    try:
        # Returns a dictionary of times
        cookingTimes = bsObj.find("div", {"class": "cooking-times"}).dl.children
        timeDict = {}
        for time in cookingTimes:
            if (time.name == "dt"):
                if ("total" in time.get_text().lower()):
                    totalTime = time.next_sibling.get_text()
                    totalTime = convertToMin(totalTime)
                    timeDict["total"] = totalTime
                    print("Total Time:", totalTime)
                elif ("prep" in time.get_text().lower()):
                    prepTime = time.next_sibling.get_text()
                    prepTime = convertToMin(prepTime)
                    timeDict["prep"] = prepTime
                    print ("Prep Time:", prepTime)
                elif ("cook" in time.get_text().lower()):
                    cookTime = time.next_sibling.get_text()
                    cookTime = convertToMin(cookTime)
                    timeDict["cook"] = cookTime
                    print ("Cook Time:", cookTime)
        return {"TIMES" : timeDict}
    except AttributeError:
        print ("Could not parse cooking times")
        return None
    finally:
        print()
        print()
        

def extractRecipeTitle(bsObj):
    try:
        # Obtains recipe name
        recipeName = bsObj.find("h1", {"itemprop": "name"}).get_text()
        print(recipeName)
        return {"TITLE": recipeName}
    except AttributeError:
        print ("Could not parse recipe title")
        return None
    finally:
        print()
        print()

def extractYieldAndLevel(bsObj):
    try:
        # Obtains number of servings and difficulty
        information = bsObj.find("div", {"class": "difficulty"}).findAll("dl")
        data = {}
        for raw_text in information:
            text = raw_text.get_text()
            
            if ("level" in text.lower()):
                level = text.strip().split("\n")
                level = level[-1]
                print ("Level:", level)
                data["LEVEL"] = level
            elif ("yield" in text.lower()):
                servings = text.strip().split("\n")
                servings = servings[-1]
                # Gets rid of the "serving(s)" unit
                if ("serving" in servings.lower()):
                    servings = servings[:servings.find("serving")]
                print ("Servings:", servings)
                data["SERVINGS"] = servings
        
        return data
    except AttributeError:
        print ("Could not parse servings/level")
        return None
    finally:
        print()
        print()
        
def extractAuthorAndDirections(bsObj):
    try:
        # Obtains directions excluding extra, redundant information
        EXCLUDE = ["cook time", "prep time", "yield:", "ease of preparation:", "serving:", "photograph by"]
        tags = bsObj.find("div", {"itemprop":"recipeInstructions"}).findAll("p")
        markup = ""
        author = ""
        for tag in tags:
            markup += str(tag).strip()

        # Removes the author from the directions and saves separately
        # If an author is not present, directions are found above the "<hr>" break if applicable
        copyrightMatch = "<p class=\"copyright\">"
        breakPoint = "<hr>"
        if(markup.find(copyrightMatch) != -1):
            splitIndex = markup.find(copyrightMatch)
            author = markup[splitIndex + len(copyrightMatch) :]
            author = author[:author.find("</p>")]
            print(author)
        elif(markup.find(breakPoint) != -1):
            splitIndex = markup.find(breakPoint)
        if (splitIndex != -1):
            markup = markup[:splitIndex]

        
        # Splits the markup based on paragraph tags by first replacing them with "<>"
        markup = markup.replace("<p>", "<>")
        markup = markup.replace("</p>", "<>")
        markup = markup.split("<>")
        directions = []
        for text in markup:
            text = text.strip()
            if (text == ""):
                continue
            # Replaces other tags found in each <p> tag with an empty string
            text = re.sub("<[ -~]*?>", "", text)
            if (not any(x in text.lower() for x in EXCLUDE)):
                directions.append(text)
        print(directions)
        return {"AUTHOR" : author, "DIRECTIONS" : directions}
    except AttributeError as e:
        print ("Could not parse directions")
        return None
    finally:
        print()
        print()
        
def extractCategories(bsObj):
    try:
        # Obtains categories. Because the text is contained in a javascript function, regex is used to locate
        # the <li> and <a href> tags and isolate the category (key) and category value text. This data is then stored
        # in categoryDict. One category can have multiple values (saved in a list).
        raw_categories = bsObj.find("script", {"data-popover":"categories"}).get_text()
        raw_categories = raw_categories.splitlines()

        data = {}
        valueList = []
        for category in raw_categories:
            category = category.strip()
            if ("</li>" in category):
                if ("</a>" not in category):
                    match = re.match("(^<li[\w =\"]*>)(.+)(</li>$)", category)
                    key = match.group(2).upper()
                else:
                    match = re.match("(^<li[\w =\"]*>)(<a href[\w =.\"/-]*>)(.+)(</a></li>$)", category)
                    value = match.group(3)
                    valueList.append(value)
                    # "last" ID represents the last value in that category (bc certain categories can have multiple values).
                    # In this case, resets value count
                    last = re.search("class=\"last\"" , category)
                    if (last):
                        data[key] = valueList
                        valueList = []
        print (data)
        return {"CATEGORIES" : data}
    except AttributeError:
        print ("Could not parse categories")
        return None
    finally:
        print()
        print()
        
    

# Writes to extractedRecipes text file with correct format
def dataProcessing(data, file):
    if (isinstance(data, str)):
        file.write(data + "\n")
    elif(isinstance(data, int)):
        dataProcessing(str(data), file)
    elif (isinstance(data, list)):
        for string in data:
            dataProcessing(string, file)
    elif (isinstance(data, dict)):
        for key, value in data.items():
            dataProcessing(key, file)
            dataProcessing(value, file)
            file.write("\n")

def has_href_but_no_classid(tag):
    return tag.name == "a" and tag.has_attr("href") and not (tag.has_attr("id") or tag.has_attr("class"))


def getLinks(articleUrl):
    html = urlopen("http://foodnetwork.com" + articleUrl)
    bsObj = BeautifulSoup(html, "html.parser")

    # Returns a list of BeautifulSoup tag objects with only "href"
    linkTags = bsObj.find("body").find_all(has_href_but_no_classid)
    # Obtains the href from all of the links on the page.
    linkReferences = [tag['href'] for tag in linkTags]

    # Creates a list of matches if the link belongs to the recipe folder
    match = []
    for link in linkReferences:
        if (re.match("/recipes/", link) is not None):
            match.append(link)

    # Opens the each match link and uses BeautifulSoup to determine if the page is actually a recipe
    # This is done by searching the comments and looking for a recipe pagetype
    recipes = []
    for href in match:
        url = urlopen("http://foodnetwork.com" + href)
        bsObjComment = BeautifulSoup(url, "html.parser")
        head = bsObjComment.find("head")
        if (head is not None):
            comments = bsObjComment.find("head").findAll(text = lambda text: isinstance(text, Comment))
            if ('pagetype: recipe' in comments) and (href not in recipes):
                recipes.append(href)
            
    return recipes




def main():
    txtFile = open("extractedRecipes.txt", "a")
    

    # Starts the crawler on article url specified and initializes a string to store the previous recipe
    newRecipe = "/recipes/food-network-kitchens/roast-chicken-with-spring-vegetables-recipe.html"
    previousRecipe = ""
    exampleDatabase = []
    maxDatabaseLength = 20
    countDuplicates = 0
    numRetry = 0
    
    # Continues to crawl through related recipe links until database is populated to desired length
    while (len(exampleDatabase) < maxDatabaseLength):
        print("################### new ########################")
        # Gets a list of links corresponding to recipes off of the new recipe page
        recipe_links = getLinks(newRecipe)
        print("~~~~~~~~POSSIBLE RECIPES:", len(recipe_links), "~~~~~~~~~~")
        try:
            # If there are no recipe links, gets the list of links from the previously saved page
            if (len(recipe_links) == 0):
                numRetry += 1
                recipe_links = getLinks(previousRecipe)
                # If there was only one path on the previous link, then try crawling from designated page
                if (len(recipe_links) == 0):
                    recipe_links = ["/recipes/sunny-anderson/easy-grilled-pork-chops-recipe.html"]

            # Selects a random recipe from the links generated
            while (newRecipe in exampleDatabase):
                newRecipe = recipe_links[random.randint(0, len(recipe_links)-1)]
            
                
        except Exception as e:
            print(e)
            print("..................................................................")
            print("..................................................................")
            print(".................       ERROR       ..............................")
            print("..................................................................")
            print("..................................................................")

        
        print("New: ", newRecipe)
        print("Previous: ", previousRecipe)
        try:
            html = urlopen("http://www.foodnetwork.com" + newRecipe)
        except HTTPError as e:
            print(e)
        else:

            # Checks for duplicate recipes before extracting data and populating database
            if newRecipe not in exampleDatabase:
                print("************************************")
                print("*********EXTRACTING RECIPE**********")
                print("************************************")
        
                bsObj = BeautifulSoup(html, "html.parser")
                extractFunctions = [extractRecipeTitle, extractIngredients, extractCookingTimes,
                                    extractYieldAndLevel, extractAuthorAndDirections, extractCategories]
                for f in extractFunctions:
                    data = f(bsObj)
                    if (data is None):
                        continue
                    dataProcessing(data, txtFile)

                exampleDatabase.append(newRecipe)

                # Stores the extracted recipe as the previous recipe before looking for a new one
                previousRecipe = newRecipe
            else:
                countDuplicates += 1
            
                

    # Populated database
    print("These recipes were added to your database:")
    for recipe in exampleDatabase:
        print (recipe)

    print()
    print("Duplicates skipped:", countDuplicates)
    print("Number of retries:", numRetry)

    txtFile.close()

main()
