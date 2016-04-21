import pymysql

def checkString(string):
    if (string[0] == "'" and string[-1] == "'"):
        return string
    elif ("'" in string):
        return '"' + string + '"'
    else:
        return "'" + string + "'"

def main():
    loop = "yes"
    while loop == "yes":
        # Initiates PyMySQL connection and then creates a cursor
        conn = pymysql.connect(host='127.0.0.1', port=3306, charset = 'utf8',
                           user='root', passwd= 'aznxdog94', db = 'cookbook')
        cur = conn.cursor()
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
            for row in rows:
                print (row)
            # Prompts user to select a category
            category = str(input('Enter a category: '))
            category = checkString(category)
            string = 'Select subcategory_type FROM CategorySubcategory WHERE category_type = ' + str(category)
            print("")
            # Executes and prints the list of subcategories that connects to chosen category
            print("Subcategories within " + category + " : " )
            cur.execute(string)
            rows = cur.fetchall()
            for row in rows:
                print (row)
            # Creates a string to use for the next SQL command
            subCategory = input('Enter a subcategory: ')
            subCategory = checkString(subCategory)
            selectionString = 'Select recipe_id, recipe_name FROM categorysubcategory_view WHERE subcategory_type = ' + subCategory
            print("")
            # Executes and print final query
            print("Recipe(s) in the " + subCategory + " subcategory")
            cur.execute(selectionString)
            rows = cur.fetchall()
            for row in rows:
                print (row)
            print("")
            # Need to pull directions time and ingredients
            recipe_id = str(input('Select a recipe, using the recipe id, from above: '))
            selectionString1 = 'Select ingredient_name FROM ingredient_view where recipe_id = ' + recipe_id
            selectionString2 = 'Select step_number, directions from directions where recipe_id = ' + recipe_id 
            selectionString3 = 'Select time_type, minutes from time_view where recipe_id = ' + recipe_id
            print("")
            print("Ingredients")
            cur.execute(selectionString1)
            rows = cur.fetchall()
            for row in rows:
                print (row)
            print("")
            print("Directions")
            cur.execute(selectionString2)
            rows = cur.fetchall()
            for row in rows:
                print (row)
            print("")    
            print("Time")
            cur.execute(selectionString3)
            print(cur.fetchall())
            print("")
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
            
        cur.close()
        conn.close()
main()
