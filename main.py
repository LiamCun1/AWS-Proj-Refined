import boto3
import psycopg2
from PIL import Image
import configparser

#Read config file containing database connection credentials
config = configparser.ConfigParser()
config.read('config.ini')

DB_connection = psycopg2.connect(
    database = config.get('Connection_Information', 'database_name'),
    user = config.get('Connection_Information', 'DB_USER'),
    password = config.get('Connection_Information', 'DB_PASSWORD'),
    host = config.get('Connection_Information', 'DB_HOST'),
    port = config.get('Connection_Information', 'DB_PORT')
)

#Define cursor to make changes within database
DB_cursor = DB_connection.cursor()


def lambda_handler(event, context):
    #connect to AWS s3 and navigate to bucket and object
    s3 = boto3.client('s3')
    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']

        #Skip objects that are not images until image is found
        if not object_key.startswith('\image'):
            continue

        #Use head_object to grab the metadata only from the object
        metadata = s3.head_object(Bucket=bucket_name, Key=object_key)

        #ContentType will provide the type of file it is
        file_type = metadata['ContentType']

        #ContentLength will provide the fill size in bytes 
        file_size = metadata['ContentLength']

        #Use get_object to retrieve the object data and metadata then utilize Image from PIL to get the height and width
        image_dimensions_data = s3.get_object(Bucket=bucket_name, Key=object_key)['Body']
        image_size = Image.open(image_dimensions_data)
        width, height = image_size.size

        #Dictionary to add to database
        datadict = {
            'File_Type':file_type,
            'File_Size':file_size,
            'width':width,
            'height':height,
            'File_Name':object_key
        }

        #Create table in database if the table s3_data_collection does not already exist. Assigning types of INT or CHAR
        create_table = (
            '''CREATE TABLE IF NOT EXISTS s3_data_collection (
            File_Type VARCHAR(255),
            File_Size INT,
            width INT,
            height INT,
            File_Name VARCHAR(255))'''
        )
        #Begin making changes in database
        DB_cursor.execute(create_table)

        #File insertion into the table s3_data_collection
        insert_query = (
            '''INSERT INTO s3_data_collection(File_Type, File_Size, width, height, File_Name)
            VALUES (%s, %s, %s, %s, %s)'''
        )
        DB_cursor.execute(insert_query, (
            datadict['File_Type'],
            datadict['FIle_Size'],
            datadict['width'],
            datadict['height'],
            datadict['File_Name']
        ))
    #Finalize changes, stop cursor, close connection to database
    DB_connection.commit()
    DB_cursor.close()
    DB_connection.close()

    

