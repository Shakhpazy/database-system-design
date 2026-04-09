import os

def create_database(db_name):
    print(db_name)
    if os.path.isdir(db_name):
        print(f"Error: database name: {db_name} already exists")
    else:
        os.makedirs(db_name, exist_ok=False)
        print(f"successful, database: {db_name} has been created")

def parse_input(user_input):
    user_input = user_input.strip()

    if not user_input:
        return

    if not user_input.endswith(";"):
        print("Error: Command must end with a semicolon.")
        return
    
    tokens = user_input.rstrip(";").split()
    
    if tokens[0].upper() == "CREATE" and tokens[1].upper() == "DATABASE":
        print(tokens)
        if len(tokens) == 3:
            create_database(tokens[-1])
        else:
            print("Error: Invalid command syntax, Too many arguments")
    

while True:
    user_input = input("\n>>> ")
    parse_input(user_input)
