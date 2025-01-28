# Project Name

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Setup and Installation](#setup-and-installation)
5. [Usage](#usage)
   - [Running the System](#running-the-system)
   - [Example Queries](#example-queries)
6. [License](#license)
7. [Acknowledgements](#acknowledgements)
8. [Contact](#contact)

---

## Overview

## Architecture

## Setup and Installation

Follow these steps to set up the project locally:

1. **Install Tesseract OCR**  
   For macOS, use Homebrew to install Tesseract:

   ```bash
   brew install tesseract
   ```

2. **Set Up a Virtual Environment**
   ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
   ```
3. **Confirm Tessaract**

   ```bash
   tesseract --version
   ```

4. **Instal MongoDB**

   ```bash
   brew tap mongodb/brew
   brew update
   brew install mongodb-community@8.0
   ```

5. **Run MongoDB**

   ```bash
   brew services start mongodb/brew/mongodb-community
   ```

6. **Set Up MongoDB**

   ```bash
   mongosh
   use admin
   db.createUser({
   user: "",
   pwd: "",
   roles: [ { role: "root", db: "admin" } ]
   })
   ```

7. **Create a Database**

```bash
  mongosh
  use db_name
```

7. **Ollama**

```bash
  brew install ollama
  brew services start ollama
  ollama run deepseek-r1:1.5b
```

## Usage

### Running the Frontend

1. **Run Streamlit App**
   ```bash
   streamlit run frontend/ui.py
   ```
