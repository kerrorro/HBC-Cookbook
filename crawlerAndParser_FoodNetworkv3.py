"""
Created by Caroline Chen on 4/1/16
Last Updated: 4/1/16
Description:
            This webcrawler finds and crawls through recipe articles from foodnetwork.com by capitalizing on the
            "related" recipe subsection. It will be used to populate a recipe box database with the desired number
            of recipes.

"""             

from bs4 import BeautifulSoup
from bs4 import Comment
from urllib.request import urlopen
import random
import re


def extractIngredients(bsObj):
    try:
        # Obtains list of ingredients
        ingredientList = bsObj.find("section", {"class":"ingredients-instructions recipe-instructions section"}).findAll("li", {"itemprop": "ingredients"})
        for ingredient in ingredientList:
            print(ingredient.get_text())
    except AttributeError:
        print ("Could not parse ingredients")
        pass
    finally:
        print()
        print()

def extractCookingTimes(bsObj):
    try:
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
    except AttributeError:
        print ("Could not parse cooking times")
        pass
    finally:
        print()
        print()
        

def extractRecipeTitle(bsObj):
    try:
        # Obtains recipe name
        recipeName = bsObj.find("h1", {"itemprop": "name"}).get_text()
        print(recipeName)
    except AttributeError:
        print ("Could not parse recipe title")
        pass
    finally:
        print()
        print()

def extractYieldAndLevel(bsObj):
    try:
        # Obtains number of servings and difficulty
        information = bsObj.find("div", {"class": "difficulty"}).findAll("dl")
        for text in information:
            data = text.get_text()
            
            if ("level" in data.lower()):
                level = data.strip().split("\n")
                level = level[-1]
                print ("Level:", level)
            elif ("yield" in data.lower()):
                servings = data.strip().split("\n")
                servings = servings[-1]
                print ("Servings:", servings)
    except AttributeError:
        print ("Could not parse servings/level")
        pass
    finally:
        print()
        print()
        
def extractDirections(bsObj):
    try:
        # Obtains directions
        directions = bsObj.find("div", {"itemprop":"recipeInstructions"}).findAll("p")
        for step in directions:
            print(step.get_text())
    except AttributeError:
        print ("Could not parse directions")
        pass
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
    except AttributeError:
        print ("Could not parse categories")
        pass
    finally:
        print()
        print()
        
    
def extractData(html):
    bsObj = BeautifulSoup(html, "html.parser")
    
    data = {extractIngredients(bsObj): "ingredients",
            extractCookingTimes(bsObj): "cooking times",
            extractRecipeTitle(bsObj): "recipe title",
            extractYieldAndLevel(bsObj): "servings",
            extractDirections(bsObj): "directions",
            extractCategories(bsObj): "categories"}

    for func, info in data.items():
        (lambda x: x)(func)



	


# Extracts the integers out of a string.
def extractInt(string):
    digitHolder = ""
    # Extracts number of servings from the string servingsMatch
    for ch in string:
        if (re.match('[0-9]', ch) is not None):
            digitHolder = digitHolder + ch
    digits = int(digitHolder)
    return digits


def has_href_but_no_classid(tag):
    return tag.name == "a" and tag.has_attr("href") and not (tag.has_attr("id") or tag.has_attr("class"))

# Checks if the link begins
#def match(link):
#    return lambda link: re.match("<a href=\"\/recipes\/", link)

def applyBsStringMethod(bsObj):
    return bsObj.string

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
        comments = bsObjComment.find("head").findAll(text = lambda text: isinstance(text, Comment))
        if ('pagetype: recipe' in comments) and (href not in recipes):
            recipes.append(href)
            
    return recipes




def main():

    # Starts the crawler on article url specified
    newRecipe = "/recipes/food-network-kitchens/roast-chicken-with-spring-vegetables-recipe.html"
    exampleDatabase = []
    maxDatabaseLength = 10
    countDuplicates = 0
    
    # Continues to crawl through related recipe links until database is populated to desired length.
    while (len(exampleDatabase) <= maxDatabaseLength):
        print("################### new ########################")
        previousRecipe = newRecipe
        recipe_links = getLinks(newRecipe)
        try:
            
            newRecipe = recipe_links[random.randint(0, len(recipe_links)-1)]
            while(newRecipe == previousRecipe):
                newRecipe = recipe_links[random.randint(0, len(recipe_links)-1)]
                
        #if (len(recipe_links) == 0):
        except ValueError:
            recipe_links = getLinks(previousRecipe)

        
        print("New: ", newRecipe)
        print("Previous: ", previousRecipe)
        try:
            html = urlopen("http://www.foodnetwork.com" + newRecipe)
        except HTTPError as e:
            print(e)
        else:            
            if newRecipe not in exampleDatabase:
                print("************************************")
                print("*********EXTRACTING RECIPE**********")
                print("************************************")
                extractData(html)
                exampleDatabase.append(newRecipe)
                
            # Check for duplicate recipes before populating database
            #if newRecipe not in exampleDatabase:
                
                
            # Generate new links to crawl from the "More recipes like this" section.
            # If it does not exist in the article, use the link from the previous
            # article to find a different crawl path.
            
            
            
                

    # Populated database
    for recipe in exampleDatabase:
        print (recipe)

    print()
    print("Number of duplicates skipped:", countDuplicates)

main()
