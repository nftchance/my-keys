# My Keys

> **Disclaimer of Liability.** Nothing in this Repository is to be construed as either an admission of liability or admission of wrongdoing on the part of either party (the developer or user), each of which denies any liabilities or wrongdoing on its part.

This project does not have a detailed README on purpose. If you would like to determine what is going on here I would recommend reading the code.

Usage of this tool is highly unethical. However, curiosity killed the cat and I felt even more unethical building this, and not open-sourcing it so here we are.

## Data Warning

A massive amount of data is stored locally. I highly advise not running this on your primary drive or you will run out of space quickly.

## Running

```
setup .env to mirror example.env
python -m venv venv
venv\Scripts\Activate.ps1

pip install -r requirements.txt

python manage.py migrate
python manage.py test
python manage.py runserver
```

## Targets

- [x] GitHub repos
- [ ] (Generalized) repository framework
- [ ] Twitch
    - [ ] Live Streams
    - [ ] Clips
    - [ ] Vods

## Notes

- While there is functional code to download twitch files and manage them within Python instead of a broken CLI, the output files are not currently in a state intended for human consumption. Hence, the location of `tmp` as the base architecture.
    - This is also why these files are not in your systems temp file as things often crash and it is easier to have access here especially because the odds are high that you want to do something more with them than be forced to store things in odd places.   