import jwt
from datetime import datetime, timedelta, timezone
from django.conf import settings


def generate_token(user_id, expiration=7):
    """
    Generate a JWT token for the given user ID and expiration time.
    """
    secret_key = 'django-insecure-0u&e35!@0(i^u122jxe#4z+s0rp6-t0n_n_$@pfl*hadkjz3z*'
    payload = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(days=expiration)
    }
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    token = token.decode('utf-8')
    
    return token


def verify_jwt(token: str): 
    """
    Verify the JWT token and return the user ID if it is valid.
    """
    secret_key = 'django-insecure-0u&e35!@0(i^u122jxe#4z+s0rp6-t0n_n_$@pfl*hadkjz3z*'
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None              # token已超时
    except jwt.InvalidTokenError:
        return None              # 无效的token    
    
    


