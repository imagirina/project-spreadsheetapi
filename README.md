<div id="top"></div>

<!-- PROJECT LOGO -->
<div align="center">
  <br />
  <a href="#">
    <img src="/static/img/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h2 align="center">Spreadsheet API</h2>

  <p align="center">
    <br />
    Hackbright Academy Capstone Project by 👤 <a href="https://github.com/imagirina">imagirina</a>
    <br />
    <a href="#">View Demo (soon)</a>·
    <a href="https://github.com/imagirina/project-spreadsheetapi">Project Link</a>
    <br />
    <br />
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ul style="list-style-type: none;">
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#tech-stack">Tech Stack</a></li>
        <li><a href="#database-model">Database Model</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contact">Contact</a></li>
  </ul>
</details>

<!-- ABOUT THE PROJECT -->

## About The Project

_Spreadsheet API_ is a service that allows creators to build products utilizing Google Spreadsheet as a database exposed via REST API. With the help of this service creators can focus on their MVP rather than implementing data model and backend.
[![Spreadsheet API Screen Shot][product-screenshot]](https://example.com)

### Tech Stack

<strong>Backend:</strong> Python, [Flask](https://flask.palletsprojects.com/en/2.1.x/), [PostgreSQL](https://www.postgresql.org/), [SQLAlchemy](https://www.sqlalchemy.org/), [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/)<br />
<strong>Frontend:</strong> JavaScript, [AJAX](https://developer.mozilla.org/en-US/docs/Web/Guide/AJAX), JSON, [Bootstrap](https://getbootstrap.com), HTML5, CSS3, [JQuery](https://jquery.com)<br/>
<strong>APIs:</strong> [Google Sheets API](https://developers.google.com/sheets/api/)<br />
<strong>Libraries:</strong> [Chart.js](https://www.chartjs.org/)
<br />
<br />

### Database Model

_Spreadsheet API_ is using a PostgreSQL database, with SQLAlchemy as an ORM.
[![Spreadsheet API Model Screen Shot][model-screenshot]](#)

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- GETTING STARTED -->

## Getting Started

To have this app running on your local computer, please follow the steps below:

### Prerequisites

Clone the repository:

```sh
git clone https://github.com/imagirina/project-spreadsheetapi.git
```

Create and activate virtual environment:

```sh
$ virtualenv env
$ echo env >> .gitignore
$ source env/bin/activate
```

Install dependencies:

```sh
$ pip install -r requirements.txt
```

### Installation

Obtain access credentials🔑 from [Google](https://developers.google.com/workspace/guides/create-credentials). Credentials will be used to obtain an access token from Google's authorization servers so the app can call Google Workspace APIs. Save them to a file `secrets.sh`. Your file should look something like this:

```sh
export DEV_CREDENTIALS='_'
export SCOPE="https://www.googleapis.com/auth/spreadsheets"
export FLASK_SESSION_KEY=b'_'
```

Create database `spreadsheetapi`:

```sh
$ createdb spreadsheetapi
```

Create tables for database:

```sh
$ python model.py
$ python -i model.py
$ db.create_all()
```

Run the app from the command line:

```sh
$ python server.py
```

In your web browser, navigate to:

```sh
http://localhost:5000/
```

If you want to use SQLAlchemy to query the database, run in interactive mode:

```sh
$ python -i model.py
```

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->

## Usage

Examples of how the project can be used (screenshots, code examples) (soon):

<!-- CONTACT -->

## Contact

👤 [imagirina](https://www.linkedin.com/in/iryna-brechko/)

## Show your support

Give a ⭐️ if you found this project helpful.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->

[product-screenshot]: /static/img/screenshot.png
[model-screenshot]: /static/img/screenshot.png
