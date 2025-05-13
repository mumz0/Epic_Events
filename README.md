# Epic_Events

Epic_Events is an event management application designed for secure user authentication, client management, contract and event tracking, with a text-based user interface powered by `urwid`.

## Main Features

- Secure authentication (Argon2 hashing, JWT, Fernet encryption)
- User, client, contract, and event management
- Text User Interface (TUI) with `urwid`
- MVC architecture (Models, Views, Controllers)
- Unit and integration test coverage
- Error monitoring with Sentry

## Project Structure

```
Epic_Events/
│
├── main.py                  # Application entry point
├── src/
│   ├── controllers/         # Business logic (auth, client, contract, etc.)
│   ├── models/              # SQLAlchemy data models
│   ├── repositories/        # Data access layer
│   ├── services/            # Services (authentication, user, etc.)
│   └── views/               # User interface (urwid)
├── utils/                   # Utilities and decorators
├── tests/                   # Unit and integration tests
├── database_config/         # Database configuration
├── ascii/                   # ASCII art for the interface
├── _persistent/             # Persistent files (e.g., database.db)
├── .env                     # Environment variables
├── pyproject.toml           # Poetry dependencies and configuration
└── README.md                # This file
```

## Installation

1. **Clone the repository**
   ```sh
   git clone <repo_url>
   cd Epic_Events
   ```

2. **Install dependencies**
   ```sh
   poetry install
   ```
## V env

```sh
poetry shell
```

## Running the Application

```sh
python main.py
```

## Running Tests

```sh
poetry run pytest
```

## Technologies Used

- Python 3.11+
- SQLAlchemy
- urwid
- passlib[argon2]
- cryptography (Fernet)
- PyJWT
- Sentry SDK
- Poetry

## Security

- Passwords are hashed using Argon2.
- Authentication tokens are signed (JWT) and encrypted (Fernet).
- Critical errors are reported to Sentry.

© Epic_Events