from psycopg2.extras import execute_values

def insert_data(staged_data,query, cursor):
    
    execute_values(cursor, query, staged_data)