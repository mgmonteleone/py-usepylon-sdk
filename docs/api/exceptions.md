# Exceptions Reference

## Exception Hierarchy

```
PylonError (base)
└── PylonAPIError (API errors)
    ├── PylonAuthenticationError (401)
    ├── PylonValidationError (400)
    ├── PylonNotFoundError (404)
    ├── PylonRateLimitError (429)
    └── PylonServerError (5xx)
```

## Base Exception

::: pylon.exceptions.PylonError
    options:
      show_root_heading: true

## API Errors

::: pylon.exceptions.PylonAPIError
    options:
      show_root_heading: true

::: pylon.exceptions.PylonAuthenticationError
    options:
      show_root_heading: true

::: pylon.exceptions.PylonNotFoundError
    options:
      show_root_heading: true

::: pylon.exceptions.PylonValidationError
    options:
      show_root_heading: true

::: pylon.exceptions.PylonRateLimitError
    options:
      show_root_heading: true

::: pylon.exceptions.PylonServerError
    options:
      show_root_heading: true

