"""
Created by: Caroline Chen
Date created: 4/11/16
Date late modified: 4/14/16
Description: Take a formatted txt file output by the Foodnetwork.com crawler and parser program
             and uses pymysql to populate a cookbook database.

        Note:
             Typecasting str() is used for ints that have to be concatenated to the SQL statement,
             while strDB() function is used to add '' around the text in the SQL statements.
             i.e. given: recipe_id = 1, time_type = "cook", minutes = 60

             insert("time", "recipe_id, time_type, minutes",
                       str(recipe_id) + ", " + strDB(time_type) + ", " + str(minutes))
             
            --> "INSERT INTO time (recipe_id, time_type, minutes) VALUES (1, 'cook', 60)
"""

import pymysql
import re

# Connect to database
conn = pymysql.connect(host='127.0.0.1', port=3306, charset = 'utf8',
                       user='root', passwd= '79461385258', db = 'Cookbook')
cur = conn.cursor()

# Placeholder "databases" to ensure duplicate entries are not inserted.
# Ignore is for seen measurement candidates which have been determined not to be measurements
ingredientDB = []
measurementDB = []
categoryDB = []
subcategoryDB= []
categorySubcatDB = []
IGNORE = []

def select(column, table, conditionCol = "", conditionVal = ""):
    #sql = "SELECT ingredient_id FROM ingredient WHERE ingredient_name = %s" % (title)
    sql = "SELECT %s FROM %s" % (column, table)
    if (conditionCol != ""):
        condition = " WHERE %s = %s" % (conditionCol, conditionVal)
        sql = sql + condition
    cur.execute(sql)
    print("*** EXECUTED SQL STATEMENT ***")
    print(sql)

# Updates a column for specified field.
def update(table, column, colVal, conditionCol, conditionVal):        
    cur.execute("UPDATE %s SET %s = %s WHERE %s = '%s'" % (table, column, colVal, conditionCol, conditionVal))
    cur.connection.commit()
    print("*** EXECUTED SQL STATEMENT ***")
    print("UPDATE %s SET %s = %s WHERE %s = '%s'" % (table, column, colVal, conditionCol, conditionVal))
    

# To insert multiple values into their corresponding columns, pass in as a string separated by commas
def insert(table, columns, values):
    cur.execute("INSERT INTO %s(%s) VALUES (%s)" % (table, columns, values))
    cur.connection.commit()
    print("*** EXECUTED SQL STATEMENT ***")
    print("INSERT INTO %s(%s) VALUES (%s)" % (table, columns, values))

# Used to pass variables as strings into functions that change the database
def strDB(text):
    return "'" + str(text) + "'"

# Returns a list where list[0] = quantity, list[1] = measurement unit, list[2] = ingredient name.
# Asks for user input on whether or not to include a word in the measurement table.
def processIngredient(ingredient):
    ingredient = ingredient.strip()
    quantity = re.match('[0-9][0-9./ -]*', ingredient)
    if (quantity is not None):
        quantity = re.match('[0-9][0-9./ -]*', ingredient).group(0).strip()
        # Update ingredient string without the quantity
        ingredient = ingredient[len(quantity) + 1:]

    # Selects the next word as a potential candidate for being a measurement.
    # Asks user if the word should be included as a measurement
    measurementCandidate = ingredient[:ingredient.find(" ")].lower()

    # If the candidate has already been ignored before, there is no measurement in the string
    if (measurementCandidate in IGNORE):
        measurement = None
    # If the candidate was already designated as a measurement:
    elif (measurementCandidate in measurementDB):
        measurement = measurementCandidate
    # Otherwise, the candidate has never been seen before
    else:
        validResponse = False
        response = input("'" + measurementCandidate + "' was not found in the measurement table. \n"
                              + "Do you want to add it to the table? (y/n): ")
        
        while (not validResponse):
            if (response.lower() == "y" or response.lower() == "n"):
                response = response.lower()
                validResponse = True
            else:
                response = input("Please enter (y/n): ")
    
        if (response == "y"):
            measurementDB.append(measurementCandidate)
            insert("measurement", "measurement_type", strDB(measurementCandidate))
            measurement = measurementCandidate     
        else:
            IGNORE.append(measurementCandidate)
            measurement = None
    
    # If the measurement candidate has never been seen before:
    if ((measurementCandidate not in measurementDB) and (measurementCandidate not in IGNORE)):
        validResponse = False
        response = input("'" + measurementCandidate + "' was not found in the measurement table. \n"
                              + "Do you want to add it to the table? (y/n): ")
        
        while (not validResponse):
            if (response.lower() == "y" or response.lower() == "n"):
                response = response.lower()
                validResponse = True
            else:
                response = input("Please enter (y/n): ")
    
        if (response == "y"):
            measurementDB.append(measurementCandidate)
            insert("measurement", "measurement_type", strDB(measurementCandidate))
            measurement = measurementCandidate     
        else:
            IGNORE.append(measurementCandidate)
            measurement = None

    # If the candidate has been seen but deemed not to be a measurement:
    elif (measurementCandidate in IGNORE):
        
    # If the candidate is already in the measurementDB:
    else:
        measurement = measurementCandidate
       
    # Updates the ingredient string without the measurement
    if (measurement is not None):
        ingredient = ingredient[len(measurement) + 1:]
            
    return [quantity, measurement, ingredient]



def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def is_upper(s):
    return s == s.upper()

def main():
    
    file = open('extractedRecipes.txt', 'r')
    readingRecipe = True
    while (readingRecipe):
        line = file.readline().strip()
        print ("-------------------------------------")
        print("READING:", line)
        ingredients = []
        if (line == "TITLE"):
            title = file.readline().strip()
            # Creates a field in the recipe table with null author and servings
            insert("recipe", "recipe_name", strDB(title))
            # Grabs recipe_id for the added recipe
            select("recipe_id", "recipe", conditionCol = "recipe_name", conditionVal = strDB(title))
            recipe_id = cur.fetchone()[0]
            #print("*************RECIPE_id = ", recipe_id, type(recipe_id))
        elif (line == "INGREDIENTS"):
            ingredientLine = line
            ingredientsPerRecipe = []
            while (ingredientLine != ""):
                print()
                ingredientLine = file.readline().strip()
                if (ingredientLine == ""):
                    continue
                ingredientLineComp = processIngredient(ingredientLine)
                quantity = ingredientLineComp[0]
                measurement = ingredientLineComp[1]
                ingredient = ingredientLineComp[2]
                if (ingredient not in ingredientDB):
                    insert("ingredient", "ingredient_name", strDB(ingredient))
                    
                    ingredientDB.append(ingredient)
                # Grabs ingredient_id for the added ingredient
                select("ingredient_id", "ingredient", conditionCol = "ingredient_name", conditionVal = strDB(ingredient))
                ingredient_id = cur.fetchone()[0]
                #print("*************ingredient_id = ", ingredient_id, type(ingredient_id))
                # Inserts into junction table with recipe_id, ingredient_id, measurement_type, and quantity if the ingredient isn't already listed for that recipe
                if (ingredient not in ingredientsPerRecipe):
                    ingredientsPerRecipe.append(ingredient)
                    insert("recipeingredient", "recipe_id, ingredient_id", str(recipe_id) + ", " + str(ingredient_id))
                    
                    if (quantity is not None):
                        if (measurement is not None):
                            # No null columns
                            insert("recipeingredient", "recipe_id, ingredient_id, measurement_type, quantity",
                                    str(recipe_id) + ", " + str(ingredient_id) + ", " + strDB(measurement) + ", " + strDB(quantity))
                        else:
                            # Null measurement
                            insert("recipeingredient", "recipe_id, ingredient_id, quantity",
                                    str(recipe_id) + ", " + str(ingredient_id) + ", " + strDB(quantity))
                    else:
                        if(measurement is not None):
                            # Null quantity
                            insert("recipeingredient", "recipe_id, ingredient_id, measurement_type",
                                    str(recipe_id) + ", " + str(ingredient_id) + ", " + strDB(measurement))
                        else:
                            # Null measurement and quantity
                            insert("recipeingredient", "recipe_id, ingredient_id",
                                    str(recipe_id) + ", " + str(ingredient_id))

                    
                    
        elif (line == "TIMES"):
            timeDict = {}
            # Counter is used to identify the double newline between the TIMES and SERVINGS sections
            consecNewLineCount = 0
            while (consecNewLineCount != 2):
                timeLines = file.readline().strip()
                if (timeLines == ""):
                    consecNewLineCount += 1
                    continue
                else:
                    consecNewLineCount = 0
                if (not is_number(timeLines)):
                    timeDict[timeLines] = file.readline().strip()
            for time_type, minutes in timeDict.items():
                insert("time", "recipe_id, time_type, minutes",
                       str(recipe_id) + ", " + strDB(time_type) + ", " + str(minutes))

        elif (line == "SERVINGS"):
            # Updates the recipe table with the recipe's serving
            servings = file.readline().strip()
            update("recipe", "servings", strDB(servings), "recipe_id", str(recipe_id))            
            
        elif (line == "LEVEL"):
            level = file.readline().strip()
            insert("difficulty", "recipe_id, difficulty_level",
                       str(recipe_id) + ", " + strDB(level))
            
        elif (line == "AUTHOR"):
            # Updates the recipe table with the recipe's author(s)
            author = file.readline().strip()
            update("recipe", "author_name", strDB(author), "recipe_id", str(recipe_id))
            
        elif (line == "DIRECTIONS"):
            directionLine = line
            directionList = []
            while (directionLine != ""):
                
                directionLine = file.readline().strip()
                if (directionLine == ""):
                    break
                directionList.append(directionLine)
            for i in range(len(directionList)):
                print()
                insert("directions", "recipe_id, step_number, directions",
                       str(recipe_id) + ", " + str(i+1) + ", " + strDB(directionList[i]))
                
        elif (line == "CATEGORIES"):
            consecNewLineCount = 0
            while (consecNewLineCount != 2):
                print()
                categoryLine = file.readline().strip()
                if (categoryLine == ""):
                    consecNewLineCount += 1
                    continue
                else:
                    consecNewLineCount = 0
                if (is_upper(categoryLine)):
                    if (categoryLine not in categoryDB):
                        categoryDB.append(categoryLine)
                        insert("category", "category_type", strDB(categoryLine))
                    subcategoryList = []
                    subcategoryLine = categoryLine
                    while(subcategoryLine != ""):
                        subcategoryLine = file.readline().strip()
                        if (subcategoryLine == ""):
                            consecNewLineCount += 1
                            break
                        subcategoryList.append(subcategoryLine)
                    for subcategory in subcategoryList:
                        if (subcategory not in subcategoryDB):
                            subcategoryDB.append(subcategory)
                            insert("subcategory", "subcategory_type", strDB(subcategory))
                        categorySubcategory = categoryLine + " " + subcategory
                        if (categorySubcategory not in categorySubcatDB):
                            categorySubcatDB.append(categorySubcategory)
                            insert("categorysubcategory", "category_type, subcategory_type", strDB(categoryLine) + ", " + strDB(subcategory))

        elif (line == "END"):
            readingRecipe = False
    
    file.close()
        

main()
cur.close()
conn.close()
