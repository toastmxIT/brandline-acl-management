import json
from boto3 import client as boto3_client
from cerberus import Validator
from schemas import ACL_MANAGEMENT_SCHEMA
from utils import bad_request, get_enviroment_var, ok, forbidden

ACL_MANAGEMENT_VALIDATOR = Validator(ACL_MANAGEMENT_SCHEMA)

DB_LAMBDA = '-'.join(
    [get_enviroment_var(pa) for pa in ['DB_STACK', 'DB_LAMBDA', 'LAMBDA_ENV']]
)

ALLOWED_ACTIONS = ['check-user-permissions']


def get_permissions_by_user_id(user_id):
    sql = f'''
        select pt.name
        from roles.permission_type as pt
        inner join roles.permission as p on p.permission_type_id = pt.id
        inner join roles.permission_role as pr on pr.permission_id = p.id
        inner join roles.role as r on r.id = pr.role_id
        inner join users.users as u on u.role_id = r.id
        where u.id = '{user_id}'
    '''

    msg = {
        'body': {
            'action': 'run',
            'queries': [sql]
        }
    }

    invoke_response = boto3_client('lambda',
                                    aws_access_key_id=get_enviroment_var('USER_ACCESS'),
                                    aws_secret_access_key=get_enviroment_var('USER_SECRET')).invoke(
        FunctionName=DB_LAMBDA,
        InvocationType='RequestResponse',
        Payload=json.dumps(msg)
    )

    response = json.loads(invoke_response['Payload'].read())

    if response['status_code'] == 200:
        body = json.loads(response['body'])
        return body[0]
    else:
        return None


def get_role_name_by_user_id(user_id):
    return f'''
        select r.name
        from roles.role as r
        inner join users.users as u on u.role_id = r.id
        where u.id = '{user_id}'
    '''


def lambda_handler(event, context):
    body = event["body"] if event["body"] else None

    if not body:
        return bad_request({'message': 'Event request does not contain body object'})

    if 'action' not in body:
        return bad_request({'message': 'Body does not contain \'action\' key'})

    if body["action"] not in ALLOWED_ACTIONS:
        return bad_request({'message': 'Body does not contain a valid action. Valid actions are: ' + ','.join(ALLOWED_ACTIONS)})

    if body["action"] == 'check-user-permissions':
        if ACL_MANAGEMENT_VALIDATOR.validate(body):
            # get the permission of the user
            user_permission = get_permissions_by_user_id(body["user_id"])
            if body["permission"] in user_permission:

                return ok({'authorized': 'True'})
            else:
                # else, return bad request
                return forbidden()
        else:
            return bad_request(ACL_MANAGEMENT_VALIDATOR.errors)
