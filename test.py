import sqlite3
from main import main

connection = sqlite3.connect("test.db")
cursor = connection.cursor()

cursor.execute("DROP TABLE IF EXISTS roster_test1")
cursor.execute("DROP TABLE IF EXISTS roster_test2")
cursor.execute("DROP TABLE IF EXISTS roster_test3")
cursor.execute("DROP TABLE IF EXISTS model_scores_by_zip")

cursor.execute(
    """
    CREATE TABLE model_scores_by_zip (
        zcta INT,
        food_access_score INT,
        social_isolation_score INT,
        algorex_sdoh_composite_score INT);
""")
cursor.execute("""
    INSERT INTO model_scores_by_zip (zcta, food_access_score, social_isolation_score, algorex_sdoh_composite_score)
               VALUES (1, 2, 3, 10);""")

cursor.execute("""
    INSERT INTO model_scores_by_zip (zcta, food_access_score, social_isolation_score, algorex_sdoh_composite_score)
               VALUES (2, 0, 7, 0);""")


cursor.execute(
    """
    CREATE TABLE roster_test1 (
        Person_Id INT,
        First_Name TEXT,
        Last_Name TEXT,
        Dob TEXT,
        Street_Address TEXT,
        City TEXT,
        State TEXT,
        Zip TEXT,
        eligibility_start_date TEXT,
        eligibility_end_date TEXT,
        payer TEXT );
""")

cursor.execute("""
    INSERT INTO roster_test1 (Person_Id, First_Name, eligibility_start_date, eligibility_end_date, Zip, payer)
               VALUES (1, "Eligible on Three Rosters, zip 1, Payer 1", '2000-01-01', '2050-01-01',1 , "Payer 1");""")
cursor.execute("""
    INSERT INTO roster_test1 (Person_Id, First_Name, eligibility_start_date, eligibility_end_date, Zip, payer)
               VALUES (2, "Eligible on Two Rosters, zip 1, Payer 1", '2000-01-01', '2050-01-01',1 , "Payer 1");""")
cursor.execute("""
    INSERT INTO roster_test1 (Person_Id, First_Name, eligibility_start_date, eligibility_end_date, Zip, payer)
               VALUES (3, "Eligible 1 roster, Food Iso < 2, payer 2 ", '2000-01-01', '2050-01-01', 2 , "Payer 2");""")
cursor.execute("""
    INSERT INTO roster_test1 (Person_Id, First_Name, eligibility_start_date, eligibility_end_date)
               VALUES (4, "Start and end dates are before", '2000-01-01', '2000-01-02');""")
cursor.execute("""
    INSERT INTO roster_test1 (Person_Id, First_Name, eligibility_start_date, eligibility_end_date)
               VALUES (5, "Start and end dates are after", '2050-01-01', '2050-01-02');""")
cursor.execute("""
    INSERT INTO roster_test1 (Person_Id, First_Name, eligibility_start_date, eligibility_end_date, Zip, payer)
               VALUES (6, "Eligible Wrong Date Format, zip 2, Payer 2", '01/01/2000', '02/02/2050',2 , "Payer 2");""")
cursor.execute("""
    INSERT INTO roster_test1 (Person_Id, First_Name, eligibility_start_date, eligibility_end_date)
               VALUES (7, "Wrong Date Format eligibility before", '01/01/2000', '02/02/2000');""")
cursor.execute("""
    INSERT INTO roster_test1 (Person_Id, First_Name, eligibility_start_date, eligibility_end_date)
               VALUES (8, "Wrong Date Format eligibility after", '01/01/2050', '02/02/2050');""")
cursor.execute(
    """
    CREATE TABLE roster_test2 (
        Person_Id INT,
        First_Name TEXT,
        Last_Name TEXT,
        Dob TEXT,
        Street_Address TEXT,
        City TEXT,
        State TEXT,
        Zip TEXT,
        eligibility_start_date TEXT,
        eligibility_end_date TEXT,
        payer TEXT );
""")
cursor.execute("""
               INSERT INTO roster_test2 (Person_Id, First_Name, eligibility_start_date, eligibility_end_date, Zip, payer)
               VALUES (1, "Eligible on Three Rosters, zip 1, Payer 1", '2000-01-01', '2050-01-01', 1 , "Payer 1");""")
cursor.execute("""
            INSERT INTO roster_test2 (Person_Id, First_Name, eligibility_start_date, eligibility_end_date, Zip, payer)
               VALUES (2, "Eligible on Two Rosters, zip 1, Payer 1", '2000-01-01', '2050-01-01',1 , "Payer 1");""")
cursor.execute(
    """--sql
    CREATE TABLE roster_test3 (
        Person_Id INT,
        First_Name TEXT,
        Last_Name TEXT,
        Dob TEXT,
        Street_Address TEXT,
        City TEXT,
        State TEXT,
        Zip TEXT,
        eligibility_start_date TEXT,
        eligibility_end_date TEXT,
        payer TEXT );
""")
cursor.execute("""
               INSERT INTO roster_test3 (Person_Id, First_Name, eligibility_start_date, eligibility_end_date, Zip, payer)
               VALUES (1, "Eligible on Three Rosters, zip 1, Payer 1", '2000-01-01', '2050-01-01', 1 , "Payer 1");""")
cursor.execute("""
    INSERT INTO roster_test1 (Person_Id, First_Name, eligibility_start_date, eligibility_end_date, Zip, payer)
               VALUES (3, "Eligible 1 roster, Food Iso < 2, payer 2 ", '2000-01-01', '2000-01-01', 2 , "Payer 2");""")
connection.commit()
connection.close()

main("test.db")
