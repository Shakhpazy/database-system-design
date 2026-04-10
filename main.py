import os

Current_Database = ""

def create_table(tb_name, cols):
    if Current_Database == "":
        print("Error: No database selected.")
        return
    
    table_path = f"{Current_Database}/{tb_name}.csv"
    if os.path.exists(table_path):
        print(f"Failed: Table '{tb_name}' already exists in '{Current_Database}'.")
    else:
        with open(table_path, "w") as f:
            f.write(",".join(cols) + "\n")
        print(f"Table '{tb_name}' created successfully.")


    

def delete_database(db_name):
    global Current_Database
    if os.path.isdir(db_name):
        os.removedirs(db_name)
        print(f"successful, database: {db_name} has been deleted")
        if Current_Database == db_name:
            Current_Database = ""
    else:
        print(f"Error: database: {db_name} does not exist")

def create_database(db_name):
    if os.path.isdir(db_name):
        print(f"Error: database name: {db_name} already exists")
    else:
        os.makedirs(db_name, exist_ok=False)
        print(f"successful, database: {db_name} has been created")

def use_database(db_name):
    global Current_Database
    if os.path.isdir(db_name):
        Current_Database = db_name
    else:
        print(f"Error: database: {db_name} does not exist")

def parse_input(user_input):
    user_input = user_input.strip()

    if not user_input:
        return

    if not user_input.endswith(";"):
        print("Error: Command must end with a semicolon.")
        return
    
    tokens = user_input.rstrip(";").split()

    if (len(tokens) < 2):
        """Prevents CREATE; or DROP; from breaking the code"""
        return
    if tokens[0].upper() == "USE":
        if (len(tokens) == 2):
            use_database(tokens[-1])
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
            end = user_input.rfind(")")
            if start != -1 and end != -1:
                column_stuff = user_input[start+1:end]
                columns = column_stuff.split(",")
            
            create_table(tb_name, columns)

                

        else:
            print("Error: Invalid command syntax, table name and/or columns not defined")




    

while True:
    user_input = input(f"\n({Current_Database}) >>> ")
    parse_input(user_input)
