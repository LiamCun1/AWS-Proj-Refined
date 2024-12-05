import boto3
import psycopg2
from PIL import Image
import configparser

config = configparser.RawConfigParser()
config.read('config.ini')

DB_connection = psycopg2.connect(
    database = config.get('DB_DATABASE'),
    user = config.get('DB_USER'),
    password = config.get('DB_PASSWORD'),
    host = config.get('DB_HOST'),
    port = config.get('DB_PORT')
)

DB_cursor = DB_connection.cursor()

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    for record in event['Records']:
        bucket_name = record['s3']['bucket']['name']
        object_key = record['s3']['object']['key']

        if not object_key.startswith('\image'):
            continue


        metadata = s3.head_object(Bucket=bucket_name, Key=object_key)

        file_type = metadata['ContentType']

        file_size = metadata['ContentLength']

        image_dimensions_data = s3.get_object(Bucket=bucket_name, Key=object_key)['Body']
        image_size = Image.open(image_dimensions_data)
        width, height = image_size.size

        datadict = {
            'File_Type':file_type,
            'File_Size':file_size,
            'width':width,
            'height':height,
            'File_Name':object_key
        }

        create_table = (
            '''CREATE TABLE IF NOT EXISTS s3_data_collection (
            File_Type VARCHAR(255),
            File_Size INT,
            width INT,
            height INT,
            File_Name VARCHAR(255))'''
        )
        DB_cursor.execute(create_table)

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
    DB_connection.commit()
    DB_cursor.close()

    

