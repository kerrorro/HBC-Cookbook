# HBC

# To Run:
- Create tables (statements below)
- (Optional) Run FoodNetwork_CrawlerParser_WriteToTextv2.py to generate new extractedRecipes.txt data set
- Run populateRecipeDB_singleIngreStr.py to populate database using formatted data in extractedRecipes.txt
- Create views (statements below)
- Run QueryInterface.py


# Create Statements

CREATE TABLE recipe (
        	recipe_id     	INT  	PRIMARY KEY      	AUTO_INCREMENT,
        	recipe_name   VARCHAR(255)     	NOT NULL,
        	author_name   VARCHAR(255),
servings    VARCHAR(255)
);
 
CREATE TABLE ingredient (
        	ingredient_id    INT  	PRIMARY KEY      	AUTO_INCREMENT,
        	ingredient_name     	VARCHAR(255)     	NOT NULL  	UNIQUE
);
 
CREATE TABLE time (
        	recipe_id     	INT,
        	time_type    	VARCHAR(255),
        	minutes       	INT,
        	PRIMARY KEY (recipe_id, time_type),
CONSTRAINT time_fk_recipe
FOREIGN KEY (recipe_id)
REFERENCES recipe (recipe_id)
);
 
CREATE TABLE difficulty (
recipe_id INT,
        	difficulty_level     VARCHAR(255),
        	PRIMARY KEY (recipe_id, difficulty_level),
CONSTRAINT difficulty_fk_recipe
FOREIGN KEY (recipe_id)
REFERENCES recipe (recipe_id)
);
 
CREATE TABLE category (
        	category_type         	VARCHAR(255)     	PRIMARY KEY
);
 
CREATE TABLE subcategory (
        	subcategory_type   	VARCHAR(255)     PRIMARY KEY  
);
 
CREATE TABLE directions (  
        	recipe_id INT,
        	step_number INT,
        	directions VARCHAR(1200) NOT NULL,
PRIMARY KEY (recipe_id, step_number),
        	CONSTRAINT directions_fk_recipe
FOREIGN KEY (recipe_id)
REFERENCES recipe (recipe_id)
);
 
CREATE TABLE recipeIngredient (
recipe_id     INT,
ingredient_id     INT,
        	PRIMARY KEY (recipe_id, ingredient_id),
CONSTRAINT recipeIngredient_fk_recipe
FOREIGN KEY (recipe_id)
REFERENCES recipe (recipe_id),
CONSTRAINT recipeIngredient_fk_ingredient
FOREIGN KEY (ingredient_id)
REFERENCES ingredient (ingredient_id)
);
 
CREATE TABLE recipeSubcategory (
        	recipe_id     INT,
        	subcategory_type     VARCHAR(255),
        	PRIMARY KEY (recipe_id, subcategory_type),
CONSTRAINT recipeSubcategory_fk_recipe
FOREIGN KEY (recipe_id)
REFERENCES recipe (recipe_id),
CONSTRAINT recipeSubcategory_fk_subcategory
FOREIGN KEY (subcategory_type)
REFERENCES subcategory (subcategory_type)
);
 
CREATE TABLE categorySubcategory (
        	category_type     VARCHAR(255),
        	subcategory_type     VARCHAR(255),
        	PRIMARY KEY (category_type, subcategory_type),
CONSTRAINT categorySubcategory_fk_category
FOREIGN KEY (category_type)
REFERENCES category (category_type),
CONSTRAINT categorySubcategory_fk_subcategory
FOREIGN KEY (subcategory_type)
REFERENCES subcategory (subcategory_type)
);
 


# Views 

create or replace view difficulty_view as
select r.recipe_id, recipe_name, d.difficulty_level from recipe r
inner join difficulty d on d.recipe_id = r.recipe_id; 

create or replace view ingredient_view as
select r.recipe_id, r.recipe_name, i.ingredient_name from recipe r
inner join recipeingredient ri on r.recipe_id = ri.recipe_id
inner join ingredient i on i.ingredient_id=ri.ingredient_id;

create or replace view time_view as
select r.recipe_id, r.recipe_name, t.time_type, t.minutes from recipe r
inner join time t on t.recipe_id = r.recipe_id; 

create or replace view categorysubcategory_view as
select r.recipe_id, r.recipe_name, cs.category_type, rs.subcategory_type from recipe r
inner join recipesubcategory rs on rs.recipe_id = r.recipe_id
inner join categorysubcategory cs on cs.subcategory_type=rs.subcategory_type;
