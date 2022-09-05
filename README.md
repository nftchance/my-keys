# My Keys

> **Disclaimer of Liability.** Nothing in this Repository is to be construed as either an admission of liability or admission of wrongdoing on the part of either party (the developer or user), each of which denies any liabilities or wrongdoing on its part.

This project does not have a detailed README on purpose. If you would like to determine what is going on here I would recommend reading the code.

Usage of this tool is highly unethical. However, curiosity killed the cat and I felt even more unethical building this, and not open-sourcing it so here we are.

## Running

```
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
python sync_repos.py
python sync_keys.py
```