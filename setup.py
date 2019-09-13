import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="telegramtui",
    version="0.1.1",
    author="Valery Krasnoselsky",
    author_email="valery.krasnoselsky@gmail.com",
    description="Telegram client on your console",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords='telegram telegramtui telegramcli telegram-cli telegram-tui tui',
    url="https://github.com/vtr0n/TelegramTUI",
    packages=setuptools.find_packages(),
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.4',
    install_requires=[
        "Pillow==6.1.0",
        "pyaes==1.6.1",
        "pyasn1==0.4.7",
        "PySocks==1.7.0",
        "python-aalib==0.3.2",
        "rsa==4.0",
        "Telethon==0.19.1.6",
        "windows-curses>=2.0;platform_system=='Windows'"
    ],
    entry_points={
        'console_scripts': [
            'telegramtui=telegramtui.__main__:main',
            'telegram-tui=telegramtui.__main__:main',
        ]
    },
)
