<div id="top"></div>

[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- PROJECT LOGO -->
<div align="center">
  <a href="#">
    <img src="images/logo.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Spreadsheet API</h3>

  <p align="center">
    Hackbright Academy Capstone Project by <a href="https://github.com/imagirina"><strong>Iryna Brechko »</strong></a>
    <br />
    <br />
    <a href="#">View Demo (soon)</a>·
    <a href="https://github.com/imagirina/project-spreadsheetapi">Project Link</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
- [Tech Stack](https://github.com/imagirina/project-spreadsheetapi#tech-stack)
  <ol>
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
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About The Project

[![Spreadsheet API Screen Shot][product-screenshot]](https://example.com)

_Spreadsheet API_ is a service that allows creators to build products utilizing Google Spreadsheet as a database exposed via REST API. With the help of this service creators can focus on their MVP rather than implementing data model and backend.

<p align="right">(<a href="#top">back to top</a>)</p>

### Tech Stack

Backend: Python, [Flask](https://flask.palletsprojects.com/en/2.1.x/), PostgreSQL, SQLAlchemy, Jinja2<br />
Frontend: JavaScript, AJAX, JSON, [Bootstrap](https://getbootstrap.com), HTML5, CSS3, [JQuery](https://jquery.com)<br/>
APIs: [Google Sheets API](https://developers.google.com/sheets/api/)
Libraries: [Chart.js](https://www.chartjs.org/)

### Database Model

[![Spreadsheet API Model Screen Shot][model-screenshot]](#)

_Spreadsheet API_ is using a PostgreSQL database, with SQLAlchemy as an ORM.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- GETTING STARTED -->

## Getting Started

To have this app running on your local computer, please follow the steps below:

### Prerequisites

- Clone the repository:

  ```sh
  git clone https://github.com/imagirina/project-spreadsheetapi.git
  ```

- Create and activate virtual environment:

  ```sh
  $ virtualenv env
  $ echo env >> .gitignore
  $ source env/bin/activate
  ```

- Install dependencies:
  ```sh
  $ pip install -r requirements.txt
  ```

### Installation

- Obtain access credentials🔑 from [Google](https://developers.google.com/workspace/guides/create-credentials). Credentials will be used to obtain an access token from Google's authorization servers so the app can call Google Workspace APIs. Save them to a file `secrets.sh`. Your file should look something like this:

```sh
export DEV_CREDENTIALS='your_dev_credentials.json'
export SCOPE="https://www.googleapis.com/auth/spreadsheets"
export FLASK_SESSION_KEY=b'your_unique_flask_key'
```

- Create database `spreadsheetapi`:

```sh
$ createdb spreadsheetapi
```

- Create tables for database:

```sh
$ python model.py
```

- Run the app from the command line:

```sh
$ python server.py
```

- In your web browser, navigate to:

```sh
localhost:5000
```

- If you want to use SQLAlchemy to query the database, run in interactive mode:

```sh
$ python -i model.py
```

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->

## Usage

Examples of how the project can be used (screenshots, code examples) (soon):

_Reference for more examples will be posted soon [Documentation](#)_

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- CONTACT -->

## Contact

👤 imagirina - [linkedin-url](https://www.linkedin.com/in/iryna-brechko/)

<p align="right">(<a href="#top">back to top</a>)</p>

## Show your support

Give a ⭐️ if you found this project helpful.

<!-- MARKDOWN LINKS & IMAGES -->

[linkedin-url]: https://www.linkedin.com/in/iryna-brechko/
[product-screenshot]: images/screenshot.png
[model-screenshot]: images/screenshot.png
