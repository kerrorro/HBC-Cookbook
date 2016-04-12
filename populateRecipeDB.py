import pymysql

def storeRecipe(cur, column, content):
    cur.execute("INSERT INTO recipe (column, content) VALUES (\"%s\",
    \"%s\")", (column, content))
    cur.connection.commit()

def storeIngredient(

    
def main():
    # Connect to database
    conn = pymysql.connect(host='127.0.0.1', port=3306,
                       user='root', passwd= "79461385258", db = "Cookbook")
    cur = conn.cursor()
    
    file = open('extractedRecipes.txt', 'r')
    reading = True
    while (reading):
        line = file.readline()
        if (line == "TITLE"):
            storeRecipe(cur, recipe_name, file.readline())
        if (line == "INGREDIENTS"):
        if (line == "TIMES"):
        if (line == "SERVINGS"):
        if (line == "LEVEL"):
        if (line == "AUTHOR"):
        if (line == "DIRECTIONS"):
            while (
        if (line == "CATEGORIES"):
            
            
        


print(cur.fetchone())
print(cur.fetchone())
cur.close()
conn.close()
    
main()
