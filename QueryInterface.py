import pymysql
# Initiates PyMySQL connection and then creates a cursor
conn = pymysql.connect(host='127.0.0.1', port=3306, charset = 'utf8',
                        user='root', passwd= '79461385258', db = 'cookbook')
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

# Prints out all releventa information associated with an input recipe_id
def pullRecipe(recipe_id):
    selectionString1 = 'Select ingredient_name FROM ingredient_view where recipe_id = ' + recipe_id
    selectionString2 = 'Select step_number, directions from directions where recipe_id = ' + recipe_id 
    selectionString3 = 'Select time_type, minutes from time_view where recipe_id = ' + recipe_id
    print("")
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
            # Pulls the list of possible categories to choose from
            print("Categories: ")
            cur.execute('Select * FROM Category')
            rows = cur.fetchall()
            printFormattedSQL(rows)
            # Prompts user to select a category
            category = str(input('Enter a category: '))
            category = checkString(category)
            string = 'Select subcategory_type FROM CategorySubcategory WHERE category_type = ' + str(category)
            print("")
            # Executes and prints the list of subcategories that connects to chosen category
            print("Subcategories within " + category + " : " )
            cur.execute(string)
            printFormattedSQL(cur.fetchall())
            # Creates a string to use for the next SQL command
            subCategory = input('Enter a subcategory: ')
            subCategory = checkString(subCategory)
            selectionString = 'Select recipe_id, recipe_name FROM categorysubcategory_view WHERE subcategory_type = ' + subCategory
            print("")
            # Executes and print final query
            print("Recipe(s) in the " + subCategory + " subcategory")
            cur.execute(selectionString)
            printFormattedSQL(cur.fetchall())
            print("")
            # Pulls and print the direction, ingredients and time of the recipe
            recipe_id = str(input('Select a recipe, using the recipe id, from above: '))
            pullRecipe(recipe_id)
        elif queryChoice == '2':
            # Prints a list of authors
            cur.execute('Select DISTINCT author_name FROM Recipe')
            printFormattedSQL(cur.fetchall())
            author = input('Enter a chef from above: ')
            author = "%" + author + "%"
            author = checkString(author)
            selectionString = "Select recipe_id, recipe_name FROM Recipe WHERE author_name LIKE " + author
            print("")
            cur.execute(selectionString)
            printFormattedSQL(cur.fetchall())
            recipe_id = str(input('Select a recipe, using the recipe id, from above: '))
            pullRecipe(recipe_id)
        elif queryChoice == '3':
            ingredient = input('Enter an ingredient you would like to search recipes for: ')
            ingredient = "%" + ingredient + "%"
            ingredient = checkString(ingredient)
            selectionString = "Select * FROM ingredient_view WHERE ingredient_name LIKE " + ingredient
            cur.execute(selectionString)
            printFormattedSQL(cur.fetchall())
            recipe_id = str(input('Select a recipe, using the recipe id, from above: '))
            pullRecipe(recipe_id)
        # Searches the database for recipes that have a cook time less than 60 minutes
        elif queryChoice == '4':
            max_cook_time = str(input('Enter a max cook time in minutes: '))
            cur.execute("Select * FROM time_view WHERE minutes < %s and time_type = 'cook'", max_cook_time)
            printFormattedSQL(cur.fetchall())
            recipe_id = str(input('Select a recipe, using the recipe id, from above: '))
            pullRecipe(recipe_id)
        elif queryChoice == '5':
            cur.execute('Select distinct difficulty_level FROM difficulty')
            printFormattedSQL(cur.fetchall())
            difficulty = input('Select a difficulty from above: ')
            difficulty = checkString(difficulty)
            # This might need a LIKE operator instead
            selectionString = 'Select recipe_id, recipe_name FROM difficulty_view WHERE difficulty_level = ' + difficulty
            cur.execute(selectionString)
            printFormattedSQL(cur.fetchall())
            recipe_id = str(input('Select a recipe, using the recipe id, from above: '))
            pullRecipe(recipe_id)
        yn = str(input('Would you like to continue? Enter yes or no: '))
        if yn == "no":
            loop = "no"
        elif yn == "yes":
            loop = "yes"
        else:
            while (yn != "yes" and yn != "no"):
                yn = str(input('Error. Enter yes or no: '))
                if yn == "no":
                    loop = "no"
                else:
                    loop = "yes"
            
        
main()
cur.close()
conn.close()
