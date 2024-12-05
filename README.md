# AWS-Proj

 # PENN Lambda Project  

 The purpose of this project is to create a Lambda function within AWS to check a new object added to an s3 bucket and grab the objects metadata if it is an image.  

 ## Installation  

 Use the package manager [pip](https://pip.pypa.io/en/stable) to install dependencies.  

```bash
pip install boto3; moto; psycopg2; PIL
```  

## Usage  

Clone this repository

```bash
git clone https://github.com/LiamCun1/AWS-Proj-Refined.git
cd AWS-Proj-Refined
```  

Replace variable holders in config.ini to reflect your own environment.

## Overview of Methods  

- Utilizing configparser to securely connect to database.
- Initialize s3 client and navigate to proper bucket.
- If an object does not begin with \Image do not continue with the function.
- metadata: Uses head_object to pull metadata from object in bucket to utilize for file_type and file_size.
- image_dimensions_data: Uses get_object to retrieve the object from the bucket.
- image_size: Uses Pillow to open the image and retrieve the width and height of it.
- datadict: Dictionary containing relevant data from the object to use in the database.
- create_table: Creates a new table s3_data_collection if it does not already exist.
- insert_query: Creates the query to input the data into the created table.
- DB_connection.commit: Commit changes made to database.
- DB_cursor.close: Close cursor so further changes may not be made to database.
