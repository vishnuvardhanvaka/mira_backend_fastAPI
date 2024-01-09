from pymongo import MongoClient
import os

class Database:
    def __init__(self):
        connection_url='mongodb+srv://vishnu:vishnu1$@babycare.7pgjopj.mongodb.net/?retryWrites=true&w=majority' #os.environ.get('MONGO_CONNECTION_URL')
        # print(connection_url)
        client=MongoClient(connection_url)
        #print('Client connection successful !')
        database=client.babycare
        self.login_collection=database.logins
        self.user_collection=database.userdata
        print('Successfully connected to the database !')
    

    def get_user(self,email):
        docs=self.user_collection.find()
        for doc in docs:
            if doc['email']==email:
                return doc
        return False
    def insert_user(self,user_details):
        try:
            user_details['disabled']=False
            self.user_collection.insert_one(user_details)
            return True
        except Exception as e:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Cannot insert user',
            headers={'WWW-Authenticate':'Bearer'}
        )
    def delete_user(self, email):
        try:
            self.user_collection.delete_one({'email': email})
            return True
        except Exception as e:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Cannot delete user',
            headers={'WWW-Authenticate':'Bearer'}
        )
    def update_user(self, email, updated_data):
        try:
            self.user_collection.update_one({'email': email}, {'$set': updated_data})
            return True
        except Exception as e:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Cannot update user',
            headers={'WWW-Authenticate':'Bearer'}
        )

    
        
