# Changelog

All notable changes to this project are documented here. The format of this document is based on [Keep a Changelog](https://keepachangelog.com). This project adheres to semantic versioning.

## [Unreleased]

## [v0.5.0] - 2019-08-05

### Added

- Add `backends.MultiAuth` for providing multiple authentication methods.
- `contrib.orm.ModelBasicAuth` backend.

### Changed

- Dependency on PassLib is now optional.
- Base backends were renamed:
  - `BasicAuthBackend` -> `BaseBasicAuth`
  - `BearerAuthBackend` -> `BaseTokenAuth`
- The renamed `BaseTokenAuth` now uses the `Token` header scheme instead of `Bearer`.

### Removed

- `BaseAuthenticate` was removed in favor of `BasicAuth.verify`.
- `contrib.orm.ModelAuthenticate` was removed in favor of `contrib.orm.ModelBasicAuth`.

## [v0.4.0] - 2019-07-21

### Added

- `base.helpers.BaseAuthenticate` for building authentication helpers.
- `contrib.orm.ModelAuthenticate`: a `BaseAuthenticate` implementation relying on an `orm` user model.
- `cryptography.get_random_string()` helper.
- Quickstart and examples.

### Changed

- **BREAKING** Rename `passwords` module to `cryptography`.

## [v0.3.0] - 2019-07-21

### Added

- Password hashers in `starlette_auth_toolkit.passwords`.

### Changed

- **BREAKING**: base backends are now under `.base.backends` instead of `.backends`.

## [v0.2.0] - 2019-07-14

### Added

- Bearer authentication backend (also known as "token authentication").
- Document the format of authorization headers for available backends.

### [v0.1.0] - 2019-05-12

### Added

- Basic Authentication backend.
- CI/CD pipeline.
- Changelog.
- Contributing guidelines.
- License.

[unreleased]: https://github.com/florimondmanca/starlette-auth-toolkit/compare/v0.5.0...HEAD
[v0.5.0]: https://github.com/florimondmanca/starlette-auth-toolkit/compare/v0.4.0...v0.5.0
[v0.4.0]: https://github.com/florimondmanca/starlette-auth-toolkit/compare/v0.3.0...v0.4.0
[v0.3.0]: https://github.com/florimondmanca/starlette-auth-toolkit/compare/v0.2.0...v0.3.0
[v0.2.0]: https://github.com/florimondmanca/starlette-auth-toolkit/compare/v0.1.0...v0.2.0
[v0.1.0]: https://github.com/florimondmanca/starlette-auth-toolkit/compare/48b5ffd...v0.1.0
