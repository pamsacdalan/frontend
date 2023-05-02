## Test

# Instructions
- For db credentials, place the db_credentials folder in the same level as manage.py
- Commands for requirements.txt
    - For install: pip install -r requirements.txt
    - To add new package: pip freeze > requirements.txt
- Migration commands:
    - python manage.py makemigrations
    - python manage.py migrate
- For future use (production deployment of static files): python manage.py collectstatic
    - Actually, baka kailangan nyo ata gamitin agad
- To run: python manage.py runserver
- If migrations and database structure are not synced, 
    - Update models.py
    - Once you are sure that the models.py file is now correct, run the following:
        - python manage.py makemigrations
        - python manage.py migrate --fake
        - python manage.py migrate 
            - For confirmation only. 
    - This will fake a migration to sync the migrations and database structure. 

# Project Structure
For reference on the folder structure, please see below:
https://studygyaan.com/django/best-practice-to-structure-django-project-directories-and-files