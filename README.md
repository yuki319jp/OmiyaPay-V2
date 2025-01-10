# Omiya Pay Ver.2.0
> [!IMPORTANT]
> Omiya Pay Ver. 2.0 is not compatible with existing Omiya Pay
It also uses MySQL as the database, so a separate environment needs to be built..
>
The new Omiya Pay is based on Flask and is more stable. (Previously Streamlit).

# Build Guide
gunicorn -c gunicorn.conf.py wsgi:app

```start
pip install -r requirements.txt
gunicorn -c gunicorn.conf.py wsgi:app
```
