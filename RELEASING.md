# Releasing

## Release model

- Runtime bundles are published from GitHub Actions.
- Public release notes should summarize user-visible changes, packaging changes, and any migration or rollback concerns.
- Release tags should be immutable once published.

## Tag naming

- Use stable release tags for published releases.
- Do not reuse or move an existing published tag.

## Release notes

Release notes should cover:

- runtime changes
- desktop changes
- breaking changes
- setup or packaging changes

## Before release

- confirm required workflows are green
- confirm no secrets or private endpoints are present in committed files
- confirm docs reflect the current public setup flow
