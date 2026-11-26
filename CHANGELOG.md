# Changelog

All notable changes to Grumo Store (formerly Voodoo Store) are documented here.

## [Unreleased]

## [1.0.0]

- First stable-version release under the Grumo Store identity.
- Synchronize Python and Rust package versions at 1.0.0.
- Preserve the existing on-disk format 1.0, legacy imports and recovery policy.
- Retain compatibility with the previously published 0.3.2 transition release.

### Inherited improvements

- Continued durability, quota, metrics, and binding hardening.
- Python transactions now expose atomic collection deletion; the Framework
  Runtime uses it to move fallback outbox records between native pending and
  delivered collections without splitting the commit boundary.
