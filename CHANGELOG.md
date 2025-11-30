# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-XX-XX

### Added
- Initial release
- JWT-based wrapping and unwrapping of environment variables
- CLI commands: `init`, `serve`, `wrap`, `unwrap`, `rotate`, `convert`
- `convert` command to convert `.env` files to `ghost.env` files with wrapped values
- Python API for programmatic usage
- HTTP server for serving wrapped environment variables
- Configuration management with secure key storage
- Support for reading standard `.env` files
- Comprehensive test suite

