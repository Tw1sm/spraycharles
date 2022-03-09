# Changelog

## [v1.0] - 3/9/2022
### Added
- Switched from Argpase to Click in both `analyze.py` and `spraycharles.py`
- Added support for Slack, Teams and Discord notitications via webhooks when a successful spray hit is identified
- Added `--notify` and `--webhook` arguments to support notifications
- Refactored EWS module to be a generic NTLM over HTTP module
- Added `--path` argument to support the NTLM module
- Added `ntlm_challenger.py`
- Updated `list_elements.json` for 2022
- Created `utils` folder and added spraycharles' auxiliary resources there
- Added `--pause` flag to optionally stop spraying and ask for confirmation to continue after a hit has been identified
- Begin changelog history
- Added versioning

