import pymysql

def main():
    # Initiates PyMySQL connection and then creates a cursor
    conn = pymysql.connect(host = '127.0.0.1', unix_socket = '/tmp/mysql.sock', user = 'root', passwd = '9913', db = 'Cookbook')
    cur = conn.cursor()
    # Prints the list of possible queries
    print('Choose between the following options:\n')
    print('Query 1 filters based upon categories\n')
    print('Query 2 allows you to choose select a favorite chef\n')
    print('Query 3 allows you to use a particular ingredient\n')
    print('Query 4 selects recipes whose cook times are less than 60 minutes\n')
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
        print(cur.fetchone())
        # Prompts user to select a category
        category = str(input('Enter a category: '))
        string = 'Select * FROM Category/Subcategory WHERE category_type = ' + str(category)
        # Executes and prints the list of subcategories that connects to chosen category
        cur.execute(string)
        print(cur.fetchone())
        # Creates a string to use for the next SQL command
        subCategory = input('Enter a category: ')
        selectionString = 'Select * FROM Recipe/Subcategory WHERE Subcategory = ' + subCategory
        # Executes and print final query
        cur.execute(selectionString)
        print(cur.fetchone())
        # Need to pull directions time and ingredients
        recipe_id = str(input('Select a recipe, using the recipe id, from above: '))
        selectionString1 = 'Select ingredient_name FROM ingredient_view where recipe_id = ' + recipe_id
        selectionString2 = 'Select step_number, directions from directions_view where recipe_id = ' + recipe_id 
        selectionString3 = 'Select time_type, minutes from time_view where recipe_id = ' + recipe_id
        cur.execute(selectionString1)
        print(cur.fetchone())
        cur.execute(selectionString2)
        print(cur.fetchone())
        cur.execute(selectionString3)
        print(cur.fetchone())
    elif queryChoice == '2':
        # Prints a list of authors
        cur.execute('Select DISTINCT author_name FROM Recipe')
        print(cur.fetchone())
        author = input('Enter a chef from above: ')
        # Look at inner join code to write an inner join
        selectionString = 'Select * FROM Recipe WHERE author LIKE ' + author
        cur.execute(selectionString)
        recipe_id = str(input('Select a recipe, using the recipe id, from above: '))
        selectionString1 = 'Select ingredient_name FROM ingredient_view where recipe_id = ' + recipe_id
        selectionString2 = 'Select step_number, directions from directions_view where recipe_id = ' + recipe_id 
        selectionString3 = 'Select time_type, minutes from time_view where recipe_id = ' + recipe_id
        cur.execute(selectionString1)
        print(cur.fetchone())
        cur.execute(selectionString2)
        print(cur.fetchone())
        cur.execute(selectionString3)
        print(cur.fetchone())
    elif queryChoice == '3':
        ingredient = input('Enter an ingredient you would like to search recipes for: ')
        # Finish searching for ingredients
        recipe_id = str(input('Select a recipe, using the recipe id, from above: '))
        selectionString1 = 'Select ingredient_name FROM ingredient_view where recipe_id = ' + recipe_id
        selectionString2 = 'Select step_number, directions from directions_view where recipe_id = ' + recipe_id 
        selectionString3 = 'Select time_type, minutes from time_view where recipe_id = ' + recipe_id
        cur.execute(selectionString1)
        print(cur.fetchone())
        cur.execute(selectionString2)
        print(cur.fetchone())
        cur.execute(selectionString3)
        print(cur.fetchone())
    # Searches the database for recipes that have a cook time less than 60 minutes
    elif queryChoice == '4':
        max_cook_time = str(input('Enter a max cook time in minutes: '))
        cur.execute('Select * FROM time_view WHERE minutes < %s and time_type = cook', max_cook_time)
        print(cur.fetchone())
        recipe_id = str(input('Select a recipe, using the recipe id, from above: '))
        selectionString1 = 'Select ingredient_name FROM ingredient_view where recipe_id = ' + recipe_id
        selectionString2 = 'Select step_number, directions from directions_view where recipe_id = ' + recipe_id 
        selectionString3 = 'Select time_type, minutes from time_view where recipe_id = ' + recipe_id
        cur.execute(selectionString1)
        print(cur.fetchone())
        cur.execute(selectionString2)
        print(cur.fetchone())
        cur.execute(selectionString3)
        print(cur.fetchone())
    elif queryChoice == '5':
        pass
    cur.close()
    conn.close()
main()
