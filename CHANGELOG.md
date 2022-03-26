# Changelog

## [v1.01] - 3/26/2022
### Added
- Utilize the rich library for terminal output
- Progress bar during spray attempt
- Pre-commit hooks for formatting
### Changed
- Code reformatted using black library
### Removed
- OpenVPN module

## [v1.0] - 3/9/2022
### Added
- Support for Slack, Teams and Discord notitications via webhooks when a successful spray hit is identified
- `--notify` and `--webhook` arguments to support notifications
- `--path` argument to support the NTLM module
- `ntlm_challenger.py`
- `utils` folder and added spraycharles' auxiliary resources there
- `--pause` flag to optionally stop spraying and ask for confirmation to continue after a hit has been identified
- Changelog
- Versioning
### Changed
- Switched from Argpase to Click in both `analyze.py` and `spraycharles.py`
- Updated `list_elements.json` for 2022
- Refactored EWS module to be a generic NTLM over HTTP module
