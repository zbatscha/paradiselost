# Paradise Lost

http://paradiselost.herokuapp.com/

## Inspiration
This web app was created as an interactive art piece for the ‘Words as Objects’ (VIS 321) course in Visual Arts taught by Professor Scanlan at Princeton University.

The inspiration for the piece was the global nature of the COVID-19 pandemic. Looking at the last few months, we can see a recurring pattern. Many of us, country after country, didn’t take it seriously until it arrived on our doorstep.

Maybe if we “spoke the same language” and had more empathy for people far away, we might have avoided the worst of the crisis. Our myopia was an expensive mistake; I hope we learn from it.


## How It Works
Users can input a poem, song, short story, or memory written in any language into the submission box.

Each line is translated (via the Google Cloud Translation API) into a language corresponding to a country impacted by this crisis. The probability of a language being assigned to a line is proportional to the toll the virus has had on a given country. Data is sourced from https://github.com/CSSEGISandData/COVID-19.


# Install

    $ git clone https://github.com/zbatscha/paradiselost.git
    $ cd paradiselost
    $ python -m venv venvParadise
    $ . venvParadise/bin/activate
    (venvParadise) $ pip install -r requirements.txt

### Install postgresql (macOS/Linux via Homebrew)

    $ brew install postgresql
    $ brew services start postgresql
    $ psql postgres
    postgres=# CREATE DATABASE paradiselost_test;

Protip:
To easily visualize and manipulate the development database, install a graphical client as well. For macOS users, Postico is awesome: https://eggerapps.at/postico/.

### Cloud Translation API Key
Paradise Lost makes use of Google Cloud Translation API requests. Get your Translation API Key at https://cloud.google.com/translate/docs/basic/setup-basic. Download the private key as a JSON, and place the file at the root of the Paradise Lost project directory.

### Set Environment Variables (macOS, Linux)

    (venvParadise) $ export FLASK_ENV='development'
    (venvParadise) $ export DATABASE_URL='postgresql+psycopg2://user:password@127.0.0.1:5432/paradiselost_test'
    (venvParadise) $ export GOOGLE_APPLICATION_CREDENTIALS="path/to/API_KEY.json"
    (venvParadise) $ export SECRET_KEY='yourSecretKey'

Remember to update the DATABASE_URL user and password. These are unique to the values set upon database connection. 5432 is the default port.

To easily get a SECRET_KEY (required by Flask):

    $ python
    >>> import secrets
    >>> yourSecretKey = secrets.token_hex(16)

### Populate Database

    (venvParadise) $ python setup_db.py

### Run Development Server

    (venvParadise) $ python run.py

Go to http://localhost:5000.