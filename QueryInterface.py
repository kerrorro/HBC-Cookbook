import pymysql

def checkString(string):
    if (string[0] == "'" and string[-1] == "'"):
        return string
    elif ("'" in string):
        return '"' + string + '"'
    else:
        return "'" + string + "'"

def main():
    # Initiates PyMySQL connection and then creates a cursor
    conn = pymysql.connect(host='127.0.0.1', port=3306, charset = 'utf8',
                       user='root', passwd= '79461385258', db = 'Cookbook')
    cur = conn.cursor()
    # Prints the list of possible queries
    print('Choose between the following options:\n')
    print('Query 1 filters based upon categories\n')
    print('Query 2 allows you to choose select a favorite chef\n')
    print('Query 3 allows you to use a particular ingredient\n')
    print('Query 4 selects recipes based on an inputted cook time\n')
    print('Query 5 selects recipes based upon dificulty\n')
    queryList = ['1','2','3','4','5']
    queryChoice = str(input('Input a number between 1 and 5 to choose your query: '))
    # Makes sure you select a query in the given range
    while queryChoice not in queryList:
        queryChoice = str(input('Input a number between 1 and 5 to choose your query: '))
    # If and elif statements to point the program to write the correct query
    if queryChoice == '1':
        # Pulls the list of possible categories to choose from
        cur.execute('Select * FROM Category')
        print(cur.fetchall())
        # Prompts user to select a category
        category = str(input('Enter a category: '))
        category = checkString(category)
        string = 'Select subcategory_type FROM CategorySubcategory WHERE category_type = ' + str(category)
        # Executes and prints the list of subcategories that connects to chosen category
        cur.execute(string)
        print(cur.fetchall())
        # Creates a string to use for the next SQL command
        subCategory = input('Enter a subcategory: ')
        subCategory = checkString(subCategory)
        selectionString = 'Select recipe_id, recipe_name FROM categorysubcategory_view WHERE subcategory_type = ' + subCategory
        # Executes and print final query
        cur.execute(selectionString)
        print(cur.fetchall())
        # Need to pull directions time and ingredients
        recipe_id = str(input('Select a recipe, using the recipe id, from above: '))
        selectionString1 = 'Select ingredient_name FROM ingredient_view where recipe_id = ' + recipe_id
        selectionString2 = 'Select step_number, directions from directions where recipe_id = ' + recipe_id 
        selectionString3 = 'Select time_type, minutes from time_view where recipe_id = ' + recipe_id
        cur.execute(selectionString1)
        print(cur.fetchall())
        cur.execute(selectionString2)
        print(cur.fetchall())
        cur.execute(selectionString3)
        print(cur.fetchall())
    elif queryChoice == '2':
        # Prints a list of authors
        cur.execute('Select DISTINCT author_name FROM Recipe')
        print(cur.fetchall())
        author = input('Enter a chef from above: ')
        author = "%" + author + "%"
        author = checkString(author)
        # Look at inner join code to write an inner join
        selectionString = "Select * FROM Recipe WHERE author_name LIKE " + author
        cur.execute(selectionString)
        print(cur.fetchall())
        recipe_id = str(input('Select a recipe, using the recipe id, from above: '))
        selectionString1 = 'Select ingredient_name FROM ingredient_view where recipe_id = ' + recipe_id
        selectionString2 = 'Select step_number, directions from directions where recipe_id = ' + recipe_id 
        selectionString3 = 'Select time_type, minutes from time_view where recipe_id = ' + recipe_id
        cur.execute(selectionString1)
        print(cur.fetchall())
        cur.execute(selectionString2)
        print(cur.fetchall())
        cur.execute(selectionString3)
        print(cur.fetchall())
    elif queryChoice == '3':
        ingredient = input('Enter an ingredient you would like to search recipes for: ')
        ingredient = checkString(ingredient)
        # Finish searching for ingredients
        recipe_id = str(input('Select a recipe, using the recipe id, from above: '))
        selectionString1 = 'Select ingredient_name FROM ingredient_view where recipe_id = ' + recipe_id
        selectionString2 = 'Select step_number, directions from directions where recipe_id = ' + recipe_id 
        selectionString3 = 'Select time_type, minutes from time_view where recipe_id = ' + recipe_id
        cur.execute(selectionString1)
        print(cur.fetchall())
        cur.execute(selectionString2)
        print(cur.fetchall())
        cur.execute(selectionString3)
        print(cur.fetchall())
    # Searches the database for recipes that have a cook time less than 60 minutes
    elif queryChoice == '4':
        max_cook_time = str(input('Enter a max cook time in minutes: '))
        cur.execute("Select * FROM time_view WHERE minutes < %s and time_type = 'cook'", max_cook_time)
        print(cur.fetchall())
        recipe_id = str(input('Select a recipe, using the recipe id, from above: '))
        selectionString1 = 'Select ingredient_name FROM ingredient_view where recipe_id = ' + recipe_id
        selectionString2 = 'Select step_number, directions from directions where recipe_id = ' + recipe_id 
        selectionString3 = 'Select time_type, minutes from time_view where recipe_id = ' + recipe_id
        cur.execute(selectionString1)
        print(cur.fetchall())
        cur.execute(selectionString2)
        print(cur.fetchall())
        cur.execute(selectionString3)
        print(cur.fetchall())
    elif queryChoice == '5':
        pass
    cur.close()
    conn.close()
main()