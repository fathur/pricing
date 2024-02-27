# Installation

1. Create `.env` file, to store all environment variables. 
   I already create example for you in `.env.example` just copy to `.env` and modify the content.
   ```
   $ copy .env.example .env
   ```
2. I am using _poetry_ to manage dependencies and virtual environment
   1. First install poetry from official website
   2. Install python, I am using python 3.11. Recommend installing using `pyenv`.
   3. Locate the binary of your python executable. 
      For `pyenv` user its located under `~/.pyenv/versions/3.11.*/bin/python`,
      replace `*` with an exact version.
   4. Tell `poetry` to use your python version
      ```
      $ cd /to/this-root/project/  # which contains pyproject.toml file
      $ poetry env use ~/.pyenv/versions/3.11.*/bin/python
      ```
3. Go inside virtual environment
   ```
   $ poetry shell
   ```
4. Install the dependencies
   ```
   $ poetry install
   ```
5. Migrate the database structure, make sure you fill the database connection inside `.env` file.
   ```
   $ python manage.py migrate
   ```