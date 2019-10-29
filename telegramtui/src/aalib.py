import platform

def is_aalib_support():
    """
    Currently aalib working only on Linux
    :return:
    """
    if platform.system() in ('Linux'):
        return True
    return False