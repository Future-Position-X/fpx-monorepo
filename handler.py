import json
import psycopg2
import os

def ping(event, context):
    connection = None
    try:
        connection = psycopg2.connect(os.environ.get('DATABASE_URL'))
        cursor = connection.cursor()
        sql = "SELECT * FROM collections"
        
        cursor.execute(sql)
        records = cursor.fetchall() 

        response = {
            "statusCode": 200,
            "body": json.dumps(records, default=str)
        }
    except (Exception, psycopg2.Error) as err:
        response = {
            "statusCode": 500,
            "body": json.dumps({"error", err}, default=str)
        }
    
    finally:
        #closing database connection.
        if(connection):
            cursor.close()
            connection.close()
    return response

if __name__ == "__main__":
    ping('', '')