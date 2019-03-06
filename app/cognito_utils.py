import boto3
import os
import ast 

access_key      = os.environ.get('AWS_IAM_ACCESS_KEY')
secret_key      = os.environ.get('AWS_IAM_SECRET_KEY')
user_pool_id    = os.environ.get('AWS_COGNITO_POOL_ID')
user_pool_region = 'us-east-2'

boto3_client_kwargs = {}
if access_key and secret_key:
    boto3_client_kwargs['aws_access_key_id'] = access_key
    boto3_client_kwargs['aws_secret_access_key'] = secret_key
if user_pool_region:
    boto3_client_kwargs['region_name'] = user_pool_region

boto3_client = boto3.client('cognito-idp', **boto3_client_kwargs)

def cognito_to_dict(attr_list, attr_map=None):
    if attr_map is None:
        attr_map = {}
    attr_dict = dict()
    for a in attr_list:
        name = a.get('Name')
        value = a.get('Value')
        if value in ['true', 'false']:
            value = ast.literal_eval(value.capitalize())
        name = attr_map.get(name,name)
        attr_dict[name] = value
    return attr_dict

class UserObj(object):
    def __init__(self, username, attribute_list, metadata=None, attr_map=None):
        """
        :param username:
        :param attribute_list:
        :param metadata: Dictionary of User metadata
        """
        self.username = username
        self.pk = username
        self._attr_map = {} if attr_map is None else attr_map
        self._data = cognito_to_dict(attribute_list,self._attr_map)
        self.sub = self._data.pop('sub',None)
        self.email_verified = self._data.pop('email_verified',None)
        self.phone_number_verified = self._data.pop('phone_number_verified',None)
        self._metadata = {} if metadata is None else metadata

    def __repr__(self):
        return '<{class_name}: {uni}>'.format(
            class_name=self.__class__.__name__, uni=self.__unicode__())

    def __unicode__(self):
        return self.username

    def __getattr__(self, name):
        if name in list(self.__dict__.get('_data',{}).keys()):
            return self._data.get(name)
        if name in list(self.__dict__.get('_metadata',{}).keys()):
            return self._metadata.get(name)

def get_users_from_list(listname, attr_map=None):
    """
    Returns all users that are in 'NotInDiscord' group for a user pool.
    :param attr_map:
    :return:
    """
    kwargs = {'UserPoolId': user_pool_id, 'GroupName': listname, 'Limit': 60}
    response = boto3_client.list_users_in_group(**kwargs)

    user_list = response.get("Users")
    page_token = response.get("NextToken")

    while page_token:
        kwargs['NextToken'] = page_token
        response = boto3_client.list_users_in_group(**kwargs)
        user_list.extend(response.get("Users"))
        page_token = response.get("NextToken")
    
    return [UserObj(user.get('Username'),
                                attribute_list=user.get('Attributes'),
                                metadata={'username':user.get('Username')},
                                attr_map=attr_map)
            for user in user_list]

def is_author(username):
    authors = get_users_from_list('Authors')
    for author in authors:
        print(author.username, username)
        if author.username == username:
            return True
    return False