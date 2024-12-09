import boto3
from moto import mock_aws
from PIL import Image
import unittest
from unittest.mock import MagicMock, patch
import main

#mock_aws all AWS interactions are mocks, patch replaces psycopg2.connect with mock_connection
@mock_aws
@patch('psycopg2.connect')
def test_lambda_function(self, mock_connection):
    #Intialize s3 client, create test bucket, create image to test in bucket, convert
    s3 = boto3.client('s3')
    s3.create_bucket(Bucket='test-bucket')
    bucket_image = Image.new(mode='RGB', size=(100,100))
    s3.put_object('test-bucket', 'image/test.jpeg', Body=bucket_image)

    #Create mock object for the connection
    mock_conn = MagicMock()
    #When mock_connection(psycopg2.connect) is called it will return the mock object mock_conn
    mock_connection.return_value = mock_conn
    #Same as mock_connection but returns a mock cursor
    mock_cursor = mock_conn.cursor.return_value


    event = {
        'Records': [{
            's3': {
            'bucket': {'name': 'test-bucket'},
            'object':{'key': 'image/pic.jpeg'}
        }
    }]
}
    
    context = {}

    main.lambda_handler(event, context)

    #assert that all database connections happen once
    #cursors are asserted that they are called since there are multiple instances of a cursor being called.
    mock_connection.assert_called_once()
    mock_cursor.execute.assert_called()
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_connection.close.assert_called_once()
    self.assertTrue(mock_cursor.execute.called)

#Call on the test to happen 
if __name__ == '__main__':
    unittest.main()


