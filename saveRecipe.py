from bs4 import BeautifulSoup
from bs4 import Comment
from urllib.request import urlopen
import random
import pymysql
import re

# Connect to database
conn = pymysql.connect(host='127.0.0.1', port=3306, charset = 'utf8',
                       user='root', passwd= '79461385258', db = 'Cookbook')
#cur = conn.cursor()

# Creates a list containing the string elements in the tuples obtained from database queries.
def createDBList(sql, cur):
    cur.execute(sql)
    DBtuple = cur.fetchall()
    
    database = []
    databaseDict = {}
    for item in DBtuple:
        if (len(item) == 1):
            database.append(item[0])
        elif(len(item) == 2):
            if (item[0] not in databaseDict.keys()):
                databaseDict[item[0]] = [item[1]]
            else:
                databaseDict[item[0]].append(item[1])
    if len(database) > 0:
        return database
    else:
        return databaseDict


def select(cur, column, table, conditionCol = "", conditionCol2 = "", conditionVal = "", conditionVal2 = ""):
    #sql = "SELECT ingredient_id FROM ingredient WHERE ingredient_name = %s" % (title)
    sql = "SELECT %s FROM %s" % (column, table)
    if (conditionCol != ""):
        condition = " WHERE %s = %s" % (conditionCol, conditionVal)
        if(conditionCol2 != ""):
            condition = condition + " AND %s = %s" % (conditionCol2, conditionVal2)
        sql = sql + condition
    cur.execute(sql)

# Updates a column for specified field.
def update(cur, table, column, colVal, conditionCol, conditionVal):        
    cur.execute("UPDATE %s SET %s = %s WHERE %s = '%s'" % (table, column, colVal, conditionCol, conditionVal))
    cur.connection.commit()

# To insert multiple values into their corresponding columns, pass in as a string separated by commas
def insert(cur, table, columns, values):
    cur.execute("INSERT INTO %s(%s) VALUES (%s)" % (table, columns, values))
    cur.connection.commit()

# Adds an escape for characters that will be inserted as part of MySQL statements
def escapeCharCheck(string):
    specialCharList = ["'", '"', "\\", "%", "_"]
    fixedString = ""

    for i in range(len(string)):
        if (string[i] in specialCharList):
            fixedString += "\\"
        fixedString += string[i]
    return fixedString

# Used to pass variables as strings into functions that change the database
def strDB(text):
    return "'" + str(text) + "'"

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def is_upper(s):
    return s == s.upper()

def populateDB(cur):
    file = open('recipe.txt', 'r')
    readingRecipe = True
    recipe_id = None
    while (readingRecipe):       
        line = file.readline().strip()
        ingredients = []
        if (line == "TITLE"):
            title = file.readline().strip()
            title = escapeCharCheck(title)
        
        elif (line == "AUTHOR"):
            # Updates the recipe table with the recipe's author(s)
            author = file.readline().strip()
            author = escapeCharCheck(author)
            # Check if the recipe by that author is already in the DB. There's a TypeError if the recipe cannot be queried (not in DB)
            try:
                # If fetchone doesn't raise an error, the recipe is already in the database
                select(cur, "recipe_id", "recipe", conditionCol = "recipe_name", conditionVal = strDB(title), conditionCol2 = "author_name", conditionVal2 = strDB(author))
                recipe_id = cur.fetchone()[0]
                print ("FAILED TO ADD: Recipe is already in the database (recipe_id = %s)" % recipe_id)
                print()
                break
            except TypeError:
                #TypeError occurs when cur.fetchone() has nothing to fetch (i.e. the recipe is not in the DB)
                insert(cur, "recipe", "recipe_name, author_name", strDB(title) + ", " + strDB(author))
                # Grabs the recipe id to be used in future insert statements
                select(cur, "recipe_id", "recipe", conditionCol = "recipe_name", conditionVal = strDB(title))
                recipe_id = cur.fetchone()[0]

        elif (line == "DIRECTIONS"):
            directionLine = line
            directionList = []
            while (directionLine != ""):
                directionLine = file.readline().strip()
                directionLine = escapeCharCheck(directionLine)
                if (directionLine == ""):
                    break
                directionList.append(directionLine)
            for i in range(len(directionList)):
                insert(cur, "directions", "recipe_id, step_number, directions",
                       str(recipe_id) + ", " + str(i+1) + ", " + strDB(directionList[i]))
        
        elif (line == "INGREDIENTS"):
            ingredient = line
            ingredientsPerRecipe = []
            while (ingredient != ""):
                ingredient = file.readline().strip()
                ingredient = escapeCharCheck(ingredient)
                if (ingredient == ""):
                    continue
                ingredientDB = createDBList("SELECT ingredient_name FROM ingredient", cur)
                if (ingredient not in ingredientDB):
                    insert(cur, "ingredient", "ingredient_name", strDB(ingredient))
                # Grabs ingredient_id for the added ingredient
                select(cur, "ingredient_id", "ingredient", conditionCol = "ingredient_name", conditionVal = strDB(ingredient))
                ingredient_id = cur.fetchone()[0]
                # Updates junction table with recipe_id, ingredient_id, measurement_type, and quantity if the ingredient isn't already listed for that recipe
                if (ingredient not in ingredientsPerRecipe):
                    ingredientsPerRecipe.append(ingredient)
                    insert(cur, "recipeingredient", "recipe_id, ingredient_id", str(recipe_id) + ", " + str(ingredient_id))
                   
        elif (line == "TIMES"):
            timeDict = {}
            # Counter is used to identify the double newline between the TIMES and SERVINGS sections
            consecNewLineCount = 0
            while (consecNewLineCount != 2):
                timeLines = file.readline().strip()
                timeLines = escapeCharCheck(timeLines)
                if (timeLines == ""):
                    consecNewLineCount += 1
                    continue
                else:
                    consecNewLineCount = 0
                if (not is_number(timeLines)):
                    timeDict[timeLines] = file.readline().strip()
            for time_type, minutes in timeDict.items():
                insert(cur, "time", "recipe_id, time_type, minutes",
                       str(recipe_id) + ", " + strDB(time_type) + ", " + str(minutes))

        elif (line == "SERVINGS"):
            # Updates the recipe table with the recipe's serving
            servings = file.readline().strip()
            servings = escapeCharCheck(servings)
            update(cur, "recipe", "servings", strDB(servings), "recipe_id", str(recipe_id))            
            
        elif (line == "LEVEL"):
            level = file.readline().strip()
            level = escapeCharCheck(level)
            insert(cur, "difficulty", "recipe_id, difficulty_level",
                       str(recipe_id) + ", " + strDB(level))
        
                
        elif (line == "CATEGORIES"):
            consecNewLineCount = 0
            while (consecNewLineCount != 2):
                categoryLine = file.readline().strip()
                
                if (categoryLine == ""):
                    consecNewLineCount += 1
                    continue
                else:
                    consecNewLineCount = 0
                if (is_upper(categoryLine)):
                    # Creates lists from the database to ensure no duplicate entries.
                    categoryDB = createDBList("SELECT * FROM category", cur)
                    
                    if (categoryLine not in categoryDB):
                        categoryLine = escapeCharCheck(categoryLine)
                        insert(cur, "category", "category_type", strDB(categoryLine))
                    subcategoryList = []
                    subcategoryLine = categoryLine
                    while(subcategoryLine != ""):
                        subcategoryLine = file.readline().strip()
                        subcategoryLine = escapeCharCheck(subcategoryLine)
                        if (subcategoryLine == ""):
                            consecNewLineCount += 1
                            break
                        subcategoryList.append(subcategoryLine)
                    for subcategory in subcategoryList:
                        
                        # Creates lists from the database to ensure no duplicate entries.
                        subcategoryDB= createDBList("SELECT * FROM subcategory", cur)
                        if (subcategory not in subcategoryDB):
                            insert(cur, "subcategory", "subcategory_type", strDB(subcategory))
                        # Creates lists from the database to ensure no duplicate entries.
                        categorySubcatDB = createDBList("SELECT category_type, subcategory_type FROM categorysubcategory", cur)
                        if ((categoryLine not in categorySubcatDB.keys()) or (subcategory not in categorySubcatDB[categoryLine])):
                            insert(cur, "categorysubcategory", "category_type, subcategory_type", strDB(categoryLine) + ", " + strDB(subcategory))
                        insert(cur, "recipesubcategory", "recipe_id, subcategory_type", str(recipe_id) + ", " + strDB(subcategory))
                            

        elif (line == "END"):
            readingRecipe = False
            file.close()
            return recipe_id
    
    
        


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
            
            ingredientText.append(ingredient.get_text())
        return {"INGREDIENTS":ingredientText}
    except AttributeError:
        print ("Could not parse ingredients")
        pass


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
                    
                elif ("prep" in time.get_text().lower()):
                    prepTime = time.next_sibling.get_text()
                    prepTime = convertToMin(prepTime)
                    timeDict["prep"] = prepTime
                    
                elif ("cook" in time.get_text().lower()):
                    cookTime = time.next_sibling.get_text()
                    cookTime = convertToMin(cookTime)
                    timeDict["cook"] = cookTime
                    
        return {"TIMES" : timeDict}
    except AttributeError:
        print ("Could not parse cooking times")
        return None
        

def extractRecipeTitle(bsObj):
    try:
        # Obtains recipe name
        recipeName = bsObj.find("h1", {"itemprop": "name"}).get_text()
        return {"TITLE": recipeName}
    except AttributeError:
        print ("Could not parse recipe title")
        return None


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
                data["LEVEL"] = level
            elif ("yield" in text.lower()):
                servings = text.strip().split("\n")
                servings = servings[-1]
                # Gets rid of the "serving(s)" unit
                if ("serving" in servings.lower()):
                    servings = servings[:servings.find("serving")]
                data["SERVINGS"] = servings
        
        return data
    except AttributeError:
        print ("Could not parse servings/level")
        return None

        
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
        
        return {"AUTHOR" : author, "DIRECTIONS" : directions}
    except AttributeError as e:
        print ("Could not parse directions")
        return None

        
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
        
        return {"CATEGORIES" : data}
    except AttributeError:
        print ("Could not parse categories")
        return None
 

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

def parseRecipe():
    # Asks for a url to save the recipe in the DB. Only allows foodnetwork.com recipes
    invalidInput = True
    while(invalidInput):
        print()
        urlInput = input("Enter the foodnetwork.com recipe URL: ")
        if ("foodnetwork.com" not in urlInput.lower()):
            print ("This is not a foodnetwork.com recipe")
        elif("http://" not in urlInput.lower()):
            print("Please include 'http://'")
        else:
            invalidInput = False
            
    try:
        html = urlopen(urlInput)
    except Exception as e:
            print(e)
    else:
        
        # Check if URL is a recipe page
        bsObj = BeautifulSoup(html, "html.parser")
        head = bsObj.find("head")
        if (head is not None):
            comments = bsObj.find("head").findAll(text = lambda text: isinstance(text, Comment))
            # If it's a valid recipe page, extract the info and write to "recipe.txt"
            if ('pagetype: recipe' in comments):
                txtFile = open("recipe.txt", "w")
                extractFunctions = [extractRecipeTitle, extractAuthorAndDirections, extractIngredients,
                                    extractCookingTimes, extractYieldAndLevel, extractCategories]
                for f in extractFunctions:
                    data = f(bsObj)
                    if (data is None):
                        txtFile.write("COULD NOT PARSE\n")
                        continue
                    # Author must processed first bc it's needed to grab the recipe_id. Handles random position of dict elements.
                    elif (isinstance(data, dict) and ("AUTHOR" in data.keys())):
                        dataProcessing({"AUTHOR": data["AUTHOR"]}, txtFile)
                        dataProcessing({"DIRECTIONS": data["DIRECTIONS"]}, txtFile)
                    else:
                        dataProcessing(data, txtFile)
                txtFile.write("END")
                txtFile.close()                    
            else:
                print("This page is not a text-based recipe.")
                print()
        else:
            print("Invalid URL.")
            print()


