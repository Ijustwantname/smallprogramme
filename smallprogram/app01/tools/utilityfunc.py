# 随机生成长度为6的数字字符串
import random
import string

def random_string(length=6):
    letters = string.digits
    return ''.join(random.choice(letters) for i in range(length))
    # 测试    


