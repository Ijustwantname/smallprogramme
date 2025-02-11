import hashlib

def encrypt_password(password):
    """ 
    This function takes a password as input and returns the encrypted password using SHA256 algorithm.
    """

    salt = 'django-insecure-0u&e35!@0(i^u122jxe#4z+s0rp6-t0n_n_$@pfl*hadkjz3z*'  
    obj = hashlib.md5(salt.encode('utf-8'))
    obj.update(password.encode('utf-8'))
    return obj.hexdigest()



