import os

Current_Database = ""

FILE_EXTENSION = ".csv"  # Change from ".csv" to ".txt"

def create_table(tb_name, cols):
    if Current_Database == "":
        print("Error: No database selected.")
        return
    
    # Each table is stored as a file inside its database directory
    table_path = f"{Current_Database}/{tb_name}{FILE_EXTENSION}"
    if os.path.exists(table_path):
        print(f"!Failed to create table {tb_name} because it already exists.")
    else:
        with open(table_path, "w") as f:
            f.write(",".join(cols))
        print(f"Table {tb_name} created.")

def delete_table(tb_name):
    if Current_Database == "":
        print("Error: No database selected.")
        return

    table_path = f"{Current_Database}/{tb_name}{FILE_EXTENSION}"
    if os.path.exists(table_path):
        os.remove(table_path)
        print(f"Table {tb_name} deleted.")
    else:
        print(f"!Failed to delete {tb_name} because it does not exist.")

def alter_table(tb_name, col):
    global Current_Database
    if Current_Database == "":
        print("Error: No database selected.")
        return

    table_path = f"{Current_Database}/{tb_name}{FILE_EXTENSION}"
    if os.path.exists(table_path):
        with open(table_path, "a") as f:
            f.write(", " + col)
        print(f"Table {tb_name} modified.")
    else:
        print(f"!Failed to alter {tb_name} because it does not exist.")


def delete_database(db_name):
    global Current_Database
    if os.path.isdir(db_name):
        os.removedirs(db_name)
        print(f"Database {db_name} deleted.")
        if Current_Database == db_name:
            Current_Database = ""
    else:
        print(f"!Failed to delete {db_name} because it does not exist.")

def create_database(db_name):
    if os.path.isdir(db_name):
        print(f"!Failed to create database {db_name} because it already exists.")
    else:
        os.makedirs(db_name, exist_ok=False)
        print(f"Database {db_name} created.")

def use_database(db_name):
    global Current_Database
    if os.path.isdir(db_name):
        Current_Database = db_name
        print(f"Using database {db_name}.")
    else:
        print(f"Error: database: {db_name} does not exist")

def select_table(tb_name):
    global Current_Database
    if Current_Database == "":
        print("Error: No database selected.")
        return
    
    table_path = f"{Current_Database}/{tb_name}{FILE_EXTENSION}"
    if os.path.exists(table_path):
        with open(table_path, "r") as f:
            columns = f.read().strip()
        # Convert from comma-separated to pipe-separated format for display
        # E.g., "a1 int, a2 varchar(20)" becomes "a1 int | a2 varchar(20)"
        print(" | ".join(col.strip() for col in columns.split(",")))
    else:
        print(f"!Failed to query table {tb_name} because it does not exist.")

def parse_input(user_input):
    user_input = user_input.strip()

    if not user_input:
        return

    if not user_input.endswith(";"):
        print("Error: Command must end with a semicolon.")
        return
    
    tokens = user_input.rstrip(";").split()

    if (len(tokens) < 2):
        # Skip invalid commands like "CREATE;" with no arguments
        return
    

    if tokens[0].upper() == "USE":
        if (len(tokens) == 2):
            use_database(tokens[-1])  # Get database name (last token)  # Get database name (last token)
        else:
            print("Error: Invalid command syntax, Too many arguments")
    elif tokens[0].upper() == "CREATE" and tokens[1].upper() == "DATABASE":
        if len(tokens) == 3:
            create_database(tokens[-1])
        else:
            print("Error: Invalid command syntax, Too many arguments")
    elif tokens[0].upper() == "DROP" and tokens[1].upper() == "DATABASE":
        if len(tokens) == 3:
            delete_database(tokens[-1])
        else:
            print("Error: Invalid command syntax, Too many arguments")
    elif tokens[0].upper() == "CREATE" and tokens[1].upper() == "TABLE":
        if len(tokens) >= 4:
            tb_name = tokens[2]
            columns = []
            start = user_input.find("(")
            end = user_input.rfind(")")  # rfind gets rightmost ), handles edge cases  # rfind gets rightmost ), handles edge cases
            if start != -1 and end != -1:
                column_stuff = user_input[start+1:end]
                columns = column_stuff.split(",")
            create_table(tb_name, columns)
    elif tokens[0].upper() == "DROP" and tokens[1].upper() == "TABLE":
        if len(tokens) == 3:
            delete_table(tokens[-1])
        else:
            print("Error: Invalid command syntax, Too many arguments")
    elif tokens[0].upper() == "ALTER" and tokens[1] == "TABLE":
        if len(tokens) > 5:
            tb_name = tokens[2]
            operation = tokens[3] #We shouldn't need it for this assignement
            column = tokens[4] + " " + tokens[5]  # Combine type and constraint
            alter_table(tb_name, column)
        else:
            print("Error: Invalid command syntax")
    elif tokens[0].upper() == "SELECT":
        if len(tokens) >= 4 and tokens[1].upper() == "*" and tokens[2].upper() == "FROM":
            tb_name = tokens[3]
            select_table(tb_name)
        else:
            print("Error: Invalid SELECT syntax")
    else:
        print("Error: Invalid command syntax, table name and/or columns not defined")




    

while True:
    user_input = input(f"\n({Current_Database}) >>> ")
    if user_input.lower().strip() == "exit":
        break
    parse_input(user_input)
