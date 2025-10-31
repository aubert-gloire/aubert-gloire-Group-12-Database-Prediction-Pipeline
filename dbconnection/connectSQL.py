import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

def execute_sql_file(connection, filepath):
    """
    Execute SQL file with comprehensive error handling
    """
    if not os.path.exists(filepath):
        print(f" Error: File '{filepath}' does not exist")
        return False
    
    try:
        cursor = connection.cursor()
        
        print(f" Reading SQL file: {filepath}")
        with open(filepath, 'r', encoding='utf-8') as file:
            sql_script = file.read()
        
        print(f" File size: {len(sql_script)} characters")
        
        # Split and execute
        sql_commands = [cmd.strip() for cmd in sql_script.split(';') if cmd.strip()]
        total_commands = len(sql_commands)
        
        print(f" Executing {total_commands} SQL commands...\n")
        
        success_count = 0
        error_count = 0
        
        for i, command in enumerate(sql_commands, 1):
            try:
                cursor.execute(command)
                success_count += 1
                print(f"✓ [{i}/{total_commands}] Success: {command[:60]}...")
            except Error as e:
                error_count += 1
                print(f"✗ [{i}/{total_commands}] Error: {e}")
                print(f"   Command: {command[:100]}...\n")
        
        connection.commit()
        cursor.close()
        
        print(f"\n{'='*60}")
        print(f" Execution complete!")
        print(f"   Successful: {success_count}")
        print(f"   Failed: {error_count}")
        print(f"{'='*60}")
        
        return error_count == 0
        
    except Exception as e:
        print(f" Unexpected error: {e}")
        return False

# Main execution
def main():
    try:
        # Load environment variables
        load_dotenv()
        # Connect to database
        print(" Connecting to database...")
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),  # Now safe!
            database=os.getenv('DB_NAME'),
            ssl_disabled=False
           
        )
        
        if connection.is_connected():
            print(" Connected successfully!\n")
            
            # Executing schema file
            schema_file = '../database_schema.sql'  
            
            execute_sql_file(connection, schema_file)
    
    except Error as e:
        print(f" Connection error: {e}")
    
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("\n Connection closed")

if __name__ == "__main__":
    main()