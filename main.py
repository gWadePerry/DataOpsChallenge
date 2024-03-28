""" High Level Analysis of Member data

This script creates and populates the std_member_info table 
and conducts some basic high level analysis of the data
focusing on members eligible during April 2022 
without including any duplicate entries

The --sql comments above SQL queries are used with the python-string-sql 
plugin to enable SQL syntax highlighting within Python strings
"""
import sqlite3


def standardize_roster(connection, roster):
    """
    Tame the data of the clients rosters roster
    (Currently the only issue comes up with dates not being in ISO) 
        Parameters:
            connection: SQLite connection object to the database.
            roster: the name of the table needed to be standardized
        Effects: 
            the roster given will have its eligibility_start_date and 
            eligibility_end_date put into standard ISO format (YYYY-MM-DD)
    """
    cursor = connection.cursor()
    # Fetch all dates from the roster table
    cursor.execute(f"""--sql
        UPDATE {roster}
        SET 
        eligibility_start_date = 
            CASE 
                WHEN eligibility_start_date LIKE '__/__/____' THEN SUBSTR(eligibility_start_date, 7, 4) || '-' || SUBSTR(eligibility_start_date, 1, 2) || '-' || SUBSTR(eligibility_start_date, 4, 2)
                ELSE eligibility_start_date
            END,
        eligibility_end_date = 
            CASE 
                WHEN eligibility_end_date LIKE '__/__/____' THEN SUBSTR(eligibility_end_date, 7, 4) || '-' || SUBSTR(eligibility_end_date, 1, 2) || '-' || SUBSTR(eligibility_end_date, 4, 2)
                ELSE eligibility_end_date
            END; """)
    connection.commit()


def create_std_table(connection):
    """
    Sets up the database by ensuring the `std_member_info` table exists/ creating the table if not

    Parameters:
        connection: SQLite connection object to the database.
    Effects: 
        the std_member_info table is created or if it
        already exists, no changes are made
    Notes:
        The client's customer's member IDs are treated as primary keys
        to guarantee the entries are unique
    """
    cursor = connection.cursor()
    # Create the std_member_info to the specs of the Doc
    cursor.execute("""--sql
        CREATE TABLE IF NOT EXISTS std_member_info (
                member_id INT PRIMARY KEY,
                member_first_name TEXT,
                member_last_name TEXT,
                date_of_birth DATE,
                main_address TEXT,
                city TEXT,
                state TEXT,
                zip_code TEXT, 
                payer TEXT
                );
                """)


def get_all_rosters(connection):
    """
    Returns a list of all the names of client's customer rosters as strings
    ( In the future another function could retrieve just the new roster(s) )

    Parameters:
        connection: SQLite connection object to the database.
    Return: 
        A list of strings where each string is a roster table name
    """
    cursor = connection.cursor()
    # Get all of the roster tables using the database's schema table
    # Fetch and store the roster tables names in the list tables
    cursor.execute("""--sql
                SELECT name FROM sqlite_master
                WHERE type='table' 
                AND name LIKE 'roster%';""")
    # cursor.fetchall() returns a list of tuples where each tuple only contains the table name
    # this will clean the data so its a list of strings
    return [name[0] for name in cursor.fetchall()]


def update_std_table(connection, roster):
    """ 
    Populates the std_member_info table with the data from roster
    Parameters:
        connection: SQLite connection object to the database.
        roster: name of the roster table to be added to std_member_info
    Effects: 
        std_member_info is filled with the customers from the roster
        With only customers eligible during April 2022
    Assumptions:
        We are interested in customers eligible at some point in April, not all of April 2022
        And only one row should exists per each member so the table does not include any duplicates
    """
    cursor = connection.cursor()
    cursor.execute(f"""--sql
                    REPLACE INTO std_member_info 
                            (member_id, member_first_name, member_last_name, date_of_birth, main_address, city, state, zip_code, payer)
                    SELECT 
                            Person_Id, First_Name, Last_Name, Dob, Street_Address, City, State, Zip, payer
                    FROM {roster}
                    WHERE eligibility_start_date < '2022-05-01' 
                    AND eligibility_end_date > '2022-04-01';""")


def high_level_analysis(connection):
    """
    Provides a high-level analysis of std_member_info
    Parameters:
        connection: SQLite connection object to the database.
    Outputs:
        Prints the results of a basic analyses to standard output
    Assumptions:
        We are interested in the data from std_member_info 
        (eligible in April 2022, with no duplicates)
    """
    cursor = connection.cursor()

    # How many distinct members are eligible in April 2022? #
    print("Distinct members eligible (in April 2022): ")

    # create_standard_table handled duplicates upon std_member_info creation
    # so a simple count works here
    cursor.execute(
        """SELECT COUNT(*) FROM std_member_info;""")
    count = cursor.fetchone()[0]
    print("\t", count)
    #######################################################################################

    ################ How many members were included more than once? #######################
    print("Number of members included more than once: ")

    # because create_standard_table handled duplicates when std_member_info was created
    # we have to scan back through the rosters

    # Create a Temp table to keep track of just member_ids
    cursor.execute("""--sql
        CREATE TEMPORARY TABLE IF NOT EXISTS member_ids (
            member_id INT ); """)

    # like in create_standard_table, get the roster tables using the database's schema table
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'roster%';")
    tables = cursor.fetchall()
    # Fill the member_ids table with the member_ids (same specs as std_member_info)
    for table in tables:
        roster = table[0]
        cursor.execute(f"""--sql
            INSERT INTO member_ids 
            SELECT Person_Id
            FROM {roster}
            WHERE eligibility_start_date < '2022-05-01' 
            AND eligibility_end_date > '2022-04-01';""")
    # Query -> group each member_id and count them, then
    # select only those members who appear more than once
    cursor.execute(""" --sql
        SELECT member_id, COUNT(*) as count
        FROM member_ids
        GROUP BY member_id
        HAVING COUNT(*) > 1;
        """)
    duplicates = cursor.fetchall()
    # You could loop through duplicates to print out who is appearing twice (or more)
    # but we just want the number of members
    print("\t", len(duplicates))

    # Cleanup temp table
    cursor.execute("DROP TABLE IF EXISTS member_ids")
    #######################################################################################

    ################ What is the breakdown of members by payer? ################
    print("Breakdown of members by payer:")

    cursor.execute(""" --sql
        SELECT payer, COUNT(*) as count
        FROM std_member_info
        GROUP BY payer
        HAVING COUNT(*) > 1;
        """)
    payers = cursor.fetchall()
    for payer, count in payers:
        print(f"\t{payer} - {count} members.")

    ################ How many members live in a zip code with a food_access_score lower than 2? ###
    print("Members with food_access_score < 2: ", end="")
    # Assumption: a given ZCTA will be the same as its ZIP Code

    cursor.execute(""" --sql
        SELECT COUNT(*)
        FROM std_member_info smi
        JOIN model_scores_by_zip msz ON smi.zip_code = msz.zcta
        WHERE food_access_score < 2;
        """)
    count = cursor.fetchone()[0]
    print(count)

    ################ What is the average social isolation score for the members? ##################
    print("Average social isolation score for the members: ")
    cursor.execute(""" --sql
        SELECT AVG(msz.social_isolation_score) AS av_social_iso_score
        FROM std_member_info smi
        JOIN model_scores_by_zip msz ON smi.zip_code = msz.zcta;
        """)
    average = cursor.fetchone()[0]
    print("\t", "%.2f" % average)

    ###### Which members live in the zip code with the highest algorex_sdoh_composite_score? ######
    print("Members living in the zip code with the highest algorex_sdoh_composite_scores: ")
    # get zip code with the highest algorex_sdoh_composite_scores
    cursor.execute(""" --sql
            SELECT zcta
            FROM model_scores_by_zip
            ORDER BY algorex_sdoh_composite_score 
            DESC LIMIT 1; """)
    zipcode = cursor.fetchone()[0]
    print("\tZip code: ", zipcode)
    # get members from that zip
    cursor.execute(f""" --sql
        SELECT smi.member_id, smi.member_first_name, smi.member_last_name
        FROM std_member_info smi
        WHERE smi.zip_code = {zipcode}; """)
    members = cursor.fetchall()
    for m_id, first, last in members:
        print(f"\t{m_id}- {first} {last}")


def main(database):
    """Main function handler"""
    try:
        connection = sqlite3.connect(database)

        create_std_table(connection)
        rosters = get_all_rosters(connection)
        for roster in rosters:
            standardize_roster(connection, roster)
            update_std_table(connection, roster)

        high_level_analysis(connection)
        connection.commit()
    except sqlite3.Error as err:
        print("SQLite error: ", err)
    finally:
        connection.close()


if __name__ == "__main__":
    main("interview.db")
