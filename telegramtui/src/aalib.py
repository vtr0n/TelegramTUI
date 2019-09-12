import platform

if platform.system() not in ('Darwin', 'Windows'):
    import aalib
