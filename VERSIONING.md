# Versioning

FleetOptimiser versioning adhere to the semantic versioning described in [semver](https://semver.org/).

V.major.minor.patch

- Major: breaking changes to previous versions
- Minor: changes compatible with previous versions. New methods or configuration
- Patch: bug fixes and small changes to code

After completion of a described issue, test-ready code should be tagged with a release candiate tag; `rc.x`.

E.g. `v1.0.1.rc.5-bug-update-vehicle`

When changes are validated, the release candidate is released as a new version: `` v.1.0.1``
