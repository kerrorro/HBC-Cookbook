import pymysql
# Initiates PyMySQL connection and then creates a cursor
conn = pymysql.connect(host='127.0.0.1', port=3306, charset = 'utf8',
                        user='root', passwd= 'aznxdog94', db = 'cookbook')
cur = conn.cursor()

# Adds quotes to items that need it before executed as SQL statements
def checkString(string):
    if (string[0] == "'" and string[-1] == "'"):
        return string
    elif ("'" in string):
        return '"' + string + '"'
    else:
        return "'" + string + "'"

# Prints each element from the return list of tuples obtained from cur.fetchall()
def printFormattedSQL(sqlOutput):
    for element in sqlOutput:
        print(element)
        
# Returns the sqlOutput as elements within a list
def makeList(sql):
    cur.execute(sql)
    line = cur.fetchall()
    line = str(line)
    return line.replace('(', '').replace(')', '').replace(',', '').replace('"', "'").strip("'").split("' '")

# Recipe list
def recipeList(sql):
    cur.execute(sql)
    line = cur.fetchall()
    recipe_id_list = []
    for element in line:
        recipe_id_list.append(str(element[0]))
    return(recipe_id_list)
        
# Prints out all releventa information associated with an input recipe_id
def pullRecipe(recipe_id):
    selectionString1 = 'Select ingredient_name FROM ingredient_view where recipe_id = ' + recipe_id
    selectionString2 = 'Select step_number, directions from directions where recipe_id = ' + recipe_id 
    selectionString3 = 'Select time_type, minutes from time_view where recipe_id = ' + recipe_id
    print("Ingredients")
    cur.execute(selectionString1)
    printFormattedSQL(cur.fetchall())
    print("")
    print("Directions")
    cur.execute(selectionString2)
    printFormattedSQL(cur.fetchall())
    print("")    
    print("Time in minutes")
    cur.execute(selectionString3)
    printFormattedSQL(cur.fetchall())
    print("")
            
def main():
    loop = "yes"
    while loop == "yes":
        # Prints the list of possible queries
        print('HBC Cookbook\n')
        print('Choose between the following options:\n')
        print('Query 1 filters based upon categories\n')
        print('Query 2 allows you to choose select a favorite chef\n')
        print('Query 3 allows you to use a particular ingredient\n')
        print('Query 4 selects recipes based on an inputted cook time\n')
        print('Query 5 selects recipes based upon difficulty\n')
        queryList = ['1','2','3','4','5']
        queryChoice = str(input('Input a number between 1 and 5 to choose your query: '))
        # Makes sure you select a query in the given range
        while queryChoice not in queryList:
            queryChoice = str(input('Error. Input a number between 1 and 5 to choose your query: '))
        print("")
        # If and elif statements to point the program to write the correct query
        if queryChoice == '1':
            # Category Menu: Executes and prints the list of categories
            print("Categories: ")
            sql = 'Select * FROM Category'
            cur.execute(sql)
            printFormattedSQL(cur.fetchall())
            # Prompts user to select a category
            category = str(input('Enter a category: '))
            category = checkString(category)
            # Puts the categories into a list to use as a check later
            category_list = makeList(sql)
            print("")
            # Checks if user entered a category that exists
            while category.strip("'").upper() not in category_list:
                print("Error. That is not one of the categories.")
                category = str(input('Enter a category: '))
                category = checkString(category)
                print("")
            # Subcategory Menu: Executes and prints the list of subcategories that connects to chosen category
            print("Subcategories within " + category + " : " )
            # Creates a string to use for the next SQL command
            sql = 'Select subcategory_type FROM CategorySubcategory WHERE category_type = ' + str(category)
            cur.execute(sql)
            printFormattedSQL(cur.fetchall())
            subCategory = input('Enter a subcategory: ')
            subCategory = checkString(subCategory)
            # Put the subcategories into a lilst to use as a check later
            subCategory_list = makeList(sql)
            print("")
            # Checks if user entered a subcategory that exists
            while subCategory.strip("'").title() not in subCategory_list:
                print("Error. That is not one of the subcategories in " + category)
                subCategory = input('Enter a subcategory: ')
                subCategory = checkString(subCategory)
                print("")
            sql = 'Select recipe_id, recipe_name FROM categorysubcategory_view WHERE subcategory_type = ' + subCategory
            # Recipe Menu: Executes and print final query
            print("Recipe(s) in the " + subCategory + " subcategory: ")
            cur.execute(sql)
            printFormattedSQL(cur.fetchall())
            recipe_id = str(input('Select a recipe using the recipe id from above: '))
            print("")
            # Checks if user entered a recipe that exists
            while recipe_id not in recipeList(sql):
                print("Error. That is not one of the recipes in " + subCategory)
                recipe_id = str(input('Select a recipe using the recipe id from above: '))
                print("")
            # Pulls and print the direction, ingredients and time of the recipe
            pullRecipe(recipe_id)   
        elif queryChoice == '2':
            # Prints a list of authors
            cur.execute('Select DISTINCT author_name FROM Recipe')
            printFormattedSQL(cur.fetchall())
            author = input('Enter a chef from above: ')
            author = "%" + author + "%"
            author = checkString(author)
            sql = "Select recipe_id, recipe_name FROM Recipe WHERE author_name LIKE " + author
            author_list = makeList(sql)
            print("")
            # While there is no recipes with that ingredient, prompt the user
            while author_list == [''] :
                print("No recipes by chef: "+ author.replace('%', ''))
                author = input('Enter a chef from above: ')
                author = "%" + author + "%"
                author = checkString(author)
                sql = "Select recipe_id, recipe_name FROM Recipe WHERE author_name LIKE " + author
                author_list = makeList(sql)
                print("")            
            # Prints Menu of Recipes
            cur.execute(sql)
            printFormattedSQL(cur.fetchall())
            recipe_id = str(input('Select a recipe using the recipe id from above: '))
            print("")
            # Checks if user entered a recipe that exists
            while recipe_id not in recipeList(sql):
                print("Error. That is not one of the recipes by chef " + author.replace('%', ''))
                recipe_id = str(input('Select a recipe using the recipe id from above: '))
                print("")
            pullRecipe(recipe_id)
        elif queryChoice == '3':
            ingredient = input('Enter an ingredient you would like to search recipes for: ')
            ingredient = "%" + ingredient + "%"
            ingredient = checkString(ingredient)
            sql = "Select * FROM ingredient_view WHERE ingredient_name LIKE " + ingredient
            recipes_list = makeList(sql)
            print("")
            # While there is no recipes with that ingredient, prompt the user
            while recipes_list == [''] :
                print("No recipes with ingredient " + ingredient.replace('%', ''))
                ingredient = input('Enter an ingredient you would like to search recipes for: ')
                ingredient = "%" + ingredient + "%"
                ingredient = checkString(ingredient)
                sql = "Select * FROM ingredient_view WHERE ingredient_name LIKE " + ingredient
                recipes_list = makeList(sql)
                print("")
            # Prints a Menu of Recipes    
            cur.execute(sql)
            printFormattedSQL(cur.fetchall())
            recipe_id = str(input('Select a recipe using the recipe id from above: '))
            print("")
            # Checks if user entered a recipe that exists
            while recipe_id not in recipeList(sql):
                print("Error. That is not one of the recipes with the ingredient " + ingredient.replace('%', ''))
                recipe_id = str(input('Select a recipe using the recipe id from above: '))
                print("")
            pullRecipe(recipe_id)
        # Searches the database for recipes that have a cook time less than 60 minutes
        elif queryChoice == '4':
            max_cook_time = str(input('Enter a max cook time in minutes: '))
            cur.execute("Select * FROM time_view WHERE minutes < %s and time_type = 'cook'", max_cook_time)
            printFormattedSQL(cur.fetchall())
            recipe_id = str(input('Select a recipe using the recipe id from above: '))
            print("")
            # Checks if user entered a recipe that exists
            cur.execute("Select * FROM time_view WHERE minutes < %s and time_type = 'cook'", max_cook_time)
            line = cur.fetchall()
            recipe_id_list = []
            for element in line:
                recipe_id_list.append(str(element[0]))
            while recipe_id not in recipe_id_list:
                print("Error. That is not of of the recipes in range with max cook time " + max_cook_time)
                recipe_id = str(input('Select a recipe using the recipe id from above: '))
                print("")            
            pullRecipe(recipe_id)
        elif queryChoice == '5':
            sql = 'Select distinct difficulty_level FROM difficulty'
            # Difficulty Menu
            cur.execute(sql)
            printFormattedSQL(cur.fetchall())
            difficulty = input('Select a difficulty from above: ')
            difficulty = checkString(difficulty)
            print("")
            # Make a list for difficulties to use as a check
            difficulty_list = makeList(sql)
            while difficulty.strip("'").title() not in difficulty_list:
                print("Error. That is not one of the difficulty levels.")
                difficulty = input('Select a difficulty from above: ')
                difficulty = checkString(difficulty)
                print("")
            # This might need a LIKE operator instead
            sql = 'Select recipe_id, recipe_name FROM difficulty_view WHERE difficulty_level = ' + difficulty
            cur.execute(sql)
            printFormattedSQL(cur.fetchall())
            recipe_id = str(input('Select a recipe using the recipe id from above: '))
            print("")
            # Checks if user entered a recipe that exists
            while recipe_id not in recipeList(sql):
                print("Error. That is not one of the recipes with difficulty level " + difficulty)
                recipe_id = str(input('Select a recipe using the recipe id from above: '))
                print("")            
            pullRecipe(recipe_id)
        yn = str(input('Would you like to continue? Enter yes or no: '))
        while (yn != "yes" and yn != "no"):
            yn = str(input('Error. Enter yes or no: '))
            
        if yn == "no":
            loop = "no"
        else:
            loop = "yes"
            
        
main()
cur.close()
conn.close()
