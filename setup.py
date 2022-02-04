import setuptools


VERSION = '0.2.52-1'


with open("README.md", 'r') as f:
    long_description: str = f.read()


setuptools.setup(
    name='wefram',
    version=VERSION,
    author='Denis Khodus',
    author_email='deniskhodus@gmail.com',
    url='https://github.com/nf-it/wefram',
    description="Wefram web platform",
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: JavaScript",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Environment :: Web Environment",
        "Framework :: FastAPI",
    ],
    python_requires='>=3.9',
    py_modules=['wefram'],
    include_package_data=True,
    install_requires=[
        'aiofiles',
        'aioredis~=2.0',
        'aiohttp',
        'asyncpg',
        'greenlet',
        'itsdangerous',
        'pillow',
        'PyJWT',
        'pytz',
        'SQLAlchemy~=1.4',
        'starlette',
        'starlette-context',
        'uvicorn',
        'uvloop',
        'websockets',
        'python-multipart',
        'babel',
        'jinja2',
        'csscompressor',
        'jsmin',
        'ldap3',
        'aiosmtplib'
    ],
    entry_points={
        'console_scripts': [
            'create-wefram-project = wefram.manage.routines.start_project:execute',
        ]
    }
)
