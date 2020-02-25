ACL_MANAGEMENT_SCHEMA = {
    'action': {
        'required': True,
        'type': 'string'
    },
    'user_id': {
        'required': True,
        'type': 'string'
    },
    'permission': {
        'required': True,
        'type': 'string',
        'allowed': ['admin.view']
    }
}
