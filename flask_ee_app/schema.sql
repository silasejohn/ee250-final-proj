DROP TABLE IF EXISTS parkingNodes;

CREATE TABLE parkingNodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    content TEXT NOT NULL
);

CREATE TABLE parkingNodes (
    serialID INTEGER NOT NULL
    email TEXT NOT NULL
    nodeState TEXT NOT NULL
    
)


"""
CREATE TABLE sharks(id integer NOT NULL, 
                    name text NOT NULL, 
                    sharktype text NOT NULL, 
                    length integer NOT NULL);

Column Names:
id 
name 
sharktype
length

INSERT INTO sharks VALUES (1, "Sammy", "Greenland Shark", 427);

VIEW TABLES
SELECT * FROM sharks; // view whole table

SELECT * FROM sharks WHERE id IS 1; // display column where id = 1

ALTER TABLE sharks ADD COLUMN age integer; // add a column to the table 

UPDATE sharks SET age = 272 WHERE id=1; // set the age value for id = 1, shark table

DELETE FROM sharks WHERE age <= 200; // delete every row for this is true

CREATE TABLE endangered (id integer NOT NULL, status text NOT NULL);
INSERT INTO endangered VALUES (1,  "near threatened");


?? CODE ??

import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
            ('First Post', 'Content for the first post')
            )

cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
            ('Second Post', 'Content for the second post')
            )

connection.commit()
connection.close()

"""