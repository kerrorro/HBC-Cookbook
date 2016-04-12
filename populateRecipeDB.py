"""
Created by: Caroline Chen
Date created: 4/11/16
Date late modified: 4/12/16
Description: Take a formatted txt file output by the Foodnetwork.com crawler and parser program
             and uses pymysql to populate a cookbook database.
"""

import pymysql
import re

# Connect to database
conn = pymysql.connect(host='127.0.0.1', port=3306, charset = 'utf8'
                       user='root', passwd= '79461385258', db = 'Cookbook')
cur = conn.cursor()


# To insert multiple values into their corresponding columns, pass in as a string separated by commas
def insert(table, columns, values):
    #if (isinstance(value, str)):
    #    print(("INSERT INTO %s (%s) VALUES ('%s')" % (table, columns, values)))
    #elif(isinstance(value, int)):
    #    print(("INSERT INTO %s (%s) VALUES (%s)" % (table, columns, values)))
    cur.execute(("INSERT INTO %s (%s) VALUES (%s)" % (table, columns, values)))
    cur.connection.commit()

# Used to pass variables as strings into functions that change the database
def strDB(string):
    return "'" + string + "'"

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
    measurementCandidate = ingredient[:ingredient.find(" ")]
    cur.execute ("SELECT measurement_type FROM measurement")
    measurementDB = cur.fetchall()
    
    if (measurementCandidate not in measurementDB):
        validResponse = False
        response = input(measurementCandidate + " was not found in the measurement table. \n"
                              + "Do you want to add it to the table? (y/n): ")
        
        while (not validResponse):
            if (response.lower() == "y" or response.lower() == "n"):
                response = response.lower()
                validResponse = True
            else:
                response = input("Please enter (y/n): ")
    
        if (response == "y"):
            insert("measurement", "measurement_type", strDB(measurementCandidate))
            measurement = measurementCandidate     
        else:
            measurement = None
            
    # If the candidate is already in the measurementDB
    else:
        measurement = measurementCandidate
            
    # Updates the ingredient string without the measurement
    if (measurement is not None):
        ingredient = ingredient[len(measurement) + 1:]
            
    return [quantity, measurement, ingredient]


def processTimes(line):
    while(line != "SERVINGS"):
        line = line

def processCategories():
    pass

def main():
    
    file = open('extractedRecipes.txt', 'r')
    readingRecipe = True
    while (readingRecipe):
        line = file.readline()
        ingredients = []
        if (line == "TITLE"):
            title = file.readline()
            # An instance of a recipe is created when the title is obtained
            insert("recipe", "recipe_name", title)
            # Grabs recipe_id for the added recipe
            cur.execute("SELECT ingredient_id FROM ingredient WHERE ingredient_name = %s" % (title))
            recipe_id = cur.fetchall()
        if (line == "INGREDIENTS"):
            ingredientLine = file.readline()
            while (ingredientLine != ""):
                ingredientLine = file.readline()
                ingredientLineComp = processIngredient(ingredientLine)
                quantity = ingredientLineComp[0]
                measurement = ingredientLineComp[1]
                ingredient = ingredientLineComp[2]
                insert("ingredient", "ingredient_name", strDB(ingredient))
                # Grabs ingredient_id for the added ingredient
                cur.execute("SELECT ingredient_id FROM ingredient WHERE ingredient_name = %s" % (ingredient))
                ingredient_id = cur.fetchall()
                # Updates junction table with recipe_id, ingredient_id, measurement_type, and quantity
                if (quantity is not None):
                    if (measurement is not None):
                        # No null columns
                        insert("recipeingredient", "recipe_id, ingredient_id, measurement_type, quantity",
                                strDB(title) + ", " + strDB(ingredient) + ", " + strDB(measurement) + ", " + strDB(quantity))
                    else:
                        # Null measurement
                        insert("recipeingredient", "recipe_id, ingredient_id, quantity",
                                strDB(title) + ", " + strDB(ingredient) + ", " + strDB(quantity))
                else:
                    if(measurement is not None):
                        # Null quantity
                        insert("recipeingredient", "recipe_id, ingredient_id, measurement_type",
                                strDB(title) + ", " + strDB(ingredient) + ", " + strDB(measurement))
                    else:
                        # Null measurement and quantity
                        insert("recipeingredient", "recipe_id, ingredient_id",
                                strDB(title) + ", " + strDB(ingredient))    
                    
        if (line == "TIMES"):
        if (line == "SERVINGS"):
        if (line == "LEVEL"):
        if (line == "AUTHOR"):
        if (line == "DIRECTIONS"):
        elif (line == "CATEGORIES"):
        elif (line == "END"):
            reading = False
    
            
        



cur.close()
conn.close()
main()
