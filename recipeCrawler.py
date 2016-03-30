"""
Created by Caroline Chen on 3/30/16

Description:
            This webcrawler finds and crawls through recipe articles from allrecipes.com by capitalizing on the
            "related" recipe subsection. It will be used to populate a recipe box database with the desired number
            of recipes.

"""             

from bs4 import BeautifulSoup
from urllib.request import urlopen
import random
import re

def getLinks(articleUrl):
    html = urlopen("http://allrecipes.com" + articleUrl)
    bsObj = BeautifulSoup(html, "html.parser")
    recipe_links = bsObj.find("div", {"class":"right-rail column"}).findAll("a", href=re.compile('\/recipe\/[0-9]+\/'))
    distinct_hrefs = set()

    # Selects for the string associated with the 'href' id and adds it to the set
    for a in recipe_links:
        distinct_hrefs.add(a['href'])

    # Convert set back to list to support indexing upon returning
    return list(distinct_hrefs)
    

def main():

    # Starts the crawler on article url specified
    recipe_links = getLinks("/recipe/236603/chef-johns-irish-stew")

    exampleDatabase = []
    maxDatabaseLength = 10
    countDuplicates = 0
    
    # Continues to crawl through related recipe links until database is populated to desired length.
    while len(recipe_links) > 0 and len(exampleDatabase) <= maxDatabaseLength:
        newRecipe = recipe_links[random.randint(0, len(recipe_links)-1)]

        # Check for duplicate recipe
        if newRecipe in exampleDatabase:
            countDuplicates += 1
            continue
        else:
            exampleDatabase.append(newRecipe)

        recipe_links = getLinks(newRecipe)

    for recipe in exampleDatabase:
        print (recipe)

    print()
    print("Number of duplicates skipped:", countDuplicates)
    
main()
