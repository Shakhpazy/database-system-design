"""
Author: Yusuf Shakhpaz
Course: TCSS 445/545 - Database System Design
Assignment: Programming Assignment 2
"""

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
    table_path = f"{Current_Database}/{tb_name}{FILE_EXTENSION}"
    if os.path.exists(table_path):
        header, rows = read_table(table_path)
        header.append(col.strip()) # Add new col to metadata line
        # Update each existing row with a NULL or empty value for the new column
        for row in rows:
            row.append("") 
        write_table(table_path, header, rows)
        print(f"Table {tb_name} modified.")


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

# Part 2
def read_table(table_path):
    """
    Read a table file. Returns (header_list, rows_list_of_lists).
    Line 1 = column metadata, subsequent lines = records.
    """
    with open(table_path, "r") as f:
        lines = f.read().splitlines()
    if not lines:
        return [], []
    header = [col.strip() for col in lines[0].split(",")]
    rows = []
    for line in lines[1:]:
        if line.strip():
            rows.append([val.strip() for val in line.split(",")])
    return header, rows


def write_table(table_path, header, rows):
    """Write header and rows back to the table file."""
    with open(table_path, "w") as f:
        f.write(",".join(header))
        for row in rows:
            f.write("\n" + ",".join(row))


def get_col_names(header):
    """
    Extract bare column names from header definitions.
    E.g. 'pid int' -> 'pid', 'name varchar(20)' -> 'name'.
    """
    return [col.split()[0] for col in header]


# ─── WHERE clause helpers ─────────────────────────────────────────────────────

def evaluate_where(row, col_names, where_col, operator, where_val):
    """
    Return True if the row satisfies the WHERE condition.
    Supports: =, !=, <, >, <=, >=. Auto-detects numeric vs string comparison.
    """
    if where_col not in col_names:
        print(f"Error: Column '{where_col}' does not exist.")
        return False

    idx = col_names.index(where_col)
    cell = row[idx]

    # Strip surrounding quotes -> string comparison
    if where_val.startswith("'") and where_val.endswith("'"):
        where_val = where_val[1:-1]
        if operator == "=":  return cell == where_val
        if operator == "!=": return cell != where_val
        if operator == "<":  return cell <  where_val
        if operator == ">":  return cell >  where_val
        if operator == "<=": return cell <= where_val
        if operator == ">=": return cell >= where_val
    else:
        # Numeric comparison
        try:
            if operator == "=":  return float(cell) == float(where_val)
            if operator == "!=": return float(cell) != float(where_val)
            if operator == "<":  return float(cell) <  float(where_val)
            if operator == ">":  return float(cell) >  float(where_val)
            if operator == "<=": return float(cell) <= float(where_val)
            if operator == ">=": return float(cell) >= float(where_val)
        except ValueError:
            if operator == "=":  return cell == where_val
            if operator == "!=": return cell != where_val

    return False


def parse_where_clause(tokens, start_idx):
    """
    Parse 'col op val' from tokens starting at start_idx.
    Returns (where_col, operator, where_val) or (None, None, None).
    """
    remainder = " ".join(tokens[start_idx:])
    for op in ["<=", ">=", "!=", "=", "<", ">"]:
        if op in remainder:
            parts = remainder.split(op, 1)
            return parts[0].strip(), op, parts[1].strip()
    return None, None, None


# ─── DML operations ───────────────────────────────────────────────────────────

def split_values(raw):
    """
    Split comma-separated values while respecting single-quoted strings.
    """
    parts, current, in_quotes = [], "", False
    for ch in raw:
        if ch == "'":
            in_quotes = not in_quotes
            current += ch
        elif ch == "," and not in_quotes:
            parts.append(current.strip())
            current = ""
        else:
            current += ch
    if current.strip():
        parts.append(current.strip())
    return parts


def insert_into(tb_name, raw_values):
    """
    Insert a single tuple into the table from a raw values string.
    """
    if Current_Database == "":
        print("Error: No database selected.")
        return

    table_path = f"{Current_Database}/{tb_name}{FILE_EXTENSION}"
    if not os.path.exists(table_path):
        print(f"!Failed to insert into {tb_name} because it does not exist.")
        return

    header, rows = read_table(table_path)

    # Strip surrounding quotes from string values before storing
    clean_values = [v.strip().strip("'") for v in split_values(raw_values)]

    rows.append(clean_values)
    write_table(table_path, header, rows)
    print("1 new record inserted.")


def select_table(tb_name, where_col=None, operator=None, where_val=None):
    """
    Print rows from the table, optionally filtered by a WHERE clause.
    Replaces the PA1 select_table with WHERE support.
    """
    if Current_Database == "":
        print("Error: No database selected.")
        return

    table_path = f"{Current_Database}/{tb_name}{FILE_EXTENSION}"
    if not os.path.exists(table_path):
        print(f"!Failed to query table {tb_name} because it does not exist.")
        return

    header, rows = read_table(table_path)
    col_names = get_col_names(header)

    print(" | ".join(header))
    for row in rows:
        if where_col is None or evaluate_where(row, col_names, where_col, operator, where_val):
            print(" | ".join(row))


def update_table(tb_name, set_col, set_val, where_col=None, operator=None, where_val=None):
    """
    Update rows matching WHERE by setting set_col = set_val.
    """
    if Current_Database == "":
        print("Error: No database selected.")
        return

    table_path = f"{Current_Database}/{tb_name}{FILE_EXTENSION}"
    if not os.path.exists(table_path):
        print(f"!Failed to update {tb_name} because it does not exist.")
        return

    header, rows = read_table(table_path)
    col_names = get_col_names(header)

    if set_col not in col_names:
        print(f"Error: Column '{set_col}' does not exist.")
        return

    set_idx = col_names.index(set_col)
    clean_val = set_val.strip("'")

    count = 0
    for row in rows:
        if where_col is None or evaluate_where(row, col_names, where_col, operator, where_val):
            row[set_idx] = clean_val
            count += 1

    write_table(table_path, header, rows)
    print(f"{count} record{'s' if count != 1 else ''} modified.")


def delete_from(tb_name, where_col=None, operator=None, where_val=None):
    """
    Delete rows from the table that match the WHERE clause.
    """
    if Current_Database == "":
        print("Error: No database selected.")
        return

    table_path = f"{Current_Database}/{tb_name}{FILE_EXTENSION}"
    if not os.path.exists(table_path):
        print(f"!Failed to delete from {tb_name} because it does not exist.")
        return

    header, rows = read_table(table_path)
    col_names = get_col_names(header)

    kept, count = [], 0
    for row in rows:
        if where_col is not None and evaluate_where(row, col_names, where_col, operator, where_val):
            count += 1
        else:
            kept.append(row)

    write_table(table_path, header, kept)
    print(f"{count} record{'s' if count != 1 else ''} deleted.")


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
    elif tokens[0].upper() == "INSERT" and tokens[1].upper() == "INTO":
        tb_name = tokens[2]
        start = user_input.find("(")
        end = user_input.rfind(")")
        if start != -1 and end != -1:
            values_str = user_input[start+1:end]
            insert_into(tb_name, values_str)
    elif tokens[0].upper() == "SELECT":
        if len(tokens) >= 4 and tokens[1] == "*" and tokens[2].upper() == "FROM":
            tb_name = tokens[3]
            # Check if WHERE exists in the tokens
            if len(tokens) > 4 and tokens[4].upper() == "WHERE":
                w_col, w_op, w_val = parse_where_clause(tokens, 5)
                select_table(tb_name, w_col, w_op, w_val)
            else:
                select_table(tb_name)
        else:
            print("Error: Invalid SELECT syntax")
    elif tokens[0].upper() == "UPDATE":
        tb_name = tokens[1]
        if len(tokens) > 3 and tokens[2].upper() == "SET":
            # Find where the WHERE clause starts to isolate the SET part
            where_idx = -1
            for i in range(len(tokens)):
                if tokens[i].upper() == "WHERE":
                    where_idx = i
                    break
            # Extract SET column = value
            # Handle the case where there is no WHERE
            limit = where_idx if where_idx != -1 else len(tokens)
            set_segment = " ".join(tokens[3:limit])
            set_col, _, set_val = set_segment.partition("=")
            
            w_col, w_op, w_val = (None, None, None)
            if where_idx != -1:
                w_col, w_op, w_val = parse_where_clause(tokens, where_idx + 1)
            
            update_table(tb_name, set_col.strip(), set_val.strip(), w_col, w_op, w_val)
    elif tokens[0].upper() == "DELETE" and tokens[1].upper() == "FROM":
        tb_name = tokens[2]
        w_col, w_op, w_val = (None, None, None)
        if len(tokens) > 3 and tokens[3].upper() == "WHERE":
            w_col, w_op, w_val = parse_where_clause(tokens, 4)
        delete_from(tb_name, w_col, w_op, w_val)
    else:
        print("Error: Invalid command syntax, table name and/or columns not defined")


while True:
    user_input = input(f"\n({Current_Database}) >>> ")
    if user_input.lower().strip() == "exit":
        break
    parse_input(user_input)
