# Nexvion production deployment implementation plan

**Goal:** Publish this repository to https://nexvionnet.com automatically and use the supplied About Us document verbatim for the company overview, services, mission, and vision.

**Architecture:** Keep the existing static HTML site and design. GitHub Actions validates and packages only public site files, then uses a dedicated SSH key restricted to rsync into the existing Apache document root. Pushes to `main` publish; pull requests validate without deployment credentials.

**Tech stack:** HTML/CSS/JavaScript, Python standard library, GitHub Actions, OpenSSH, rsync, existing cPanel Apache.

**Spec:** User request in this chat and `About Us (1).docx`, read on 10 October 2026.

## Constraints

- Preserve the established site design, contact details, pricing, and assets.
- Use all three About paragraphs and the five services, Mission, and Vision from the supplied document.
- Introduce version 1.1.0 as the minor release of the previously unversioned site.
- Never store root credentials, deployment private keys, or repository metadata in the public directory or Git.
- Preserve `.well-known`, `php.ini`, and `.user.ini` during synchronization.
- Verify the live deployment against the exact Git commit and HTML bytes.
- `main` is the proposed production branch; an optional user preference question was sent before implementation.

## Review focus

- Packaging must reject symlinks, private files under assets, missing assets, and invalid versions before publishing.
- Deployment must preserve cPanel/AutoSSL files and keep root credentials out of GitHub.
- Branch restrictions must prevent pull requests or manually selected feature branches from publishing.
- Caching must allow visitors to see new HTML and changed assets after deployment.
- Desktop/mobile layouts, light/dark themes, and navigation must continue to work with the longer copy.

## Task 1: Content and release packaging

- [x] Add packaging tests using temporary source directories: public files only; version and commit manifest; reject symlinks/private asset files/missing references/invalid versions.
- [x] Run the tests before implementation and confirm the absent packager fails.
- [x] Update `index.html` from the DOCX, preserving paragraph text and existing visual styles.
- [x] Add `VERSION`, `.gitignore`, and `scripts/package_site.py`.
- [x] Update `.htaccess` so HTML/JSON and unversioned assets revalidate instead of remaining stale.
- [x] Run all tests and inspect the page at desktop and mobile widths in both themes.

## Task 2: Automatic deployment and live verification

- [x] Add `.github/workflows/deploy.yml`: validate PRs; serialize production pushes; pin checkout; use a restricted SSH key with pinned host identity; verify live version and HTML.
- [x] Document the production branch, publishable files, version bump, secret names, and rollback.
- [x] Review the complete diff with a fresh reviewer before publishing.
- [x] Back up the existing public directory outside the document root. Create a dedicated unprivileged deployment user and restrict its key to write-only rsync into the site directory.
- [x] Save the deployment key and known host entry in repository Actions secrets.
- [ ] Publish the reviewed commit to `main`, wait for its Actions run, and verify the public site, assets, redirects, headers, and release manifest.
- [ ] Remove temporary private keys and close the root SSH control connection.

## Execution record

Work is in a fresh clone on `codex/auto-deploy-about`, based on `origin/main`; the original workspace had no application files or commits. There is no existing test runner or build dependency. The user's explicit publication request authorizes the final GitHub push and website deployment.

Pre-publication verification: all five packaging tests passed; all supplied DOCX paragraphs and service descriptions matched exactly; desktop and mobile previews passed; fresh code review found no blocking issues. The user confirmed `main` for production, and it is now the repository default. The dedicated key rejects shell commands and read access. The macOS OpenBSD rsync client emits an unsupported `--dirs` argument; production uses GNU rsync on the GitHub Ubuntu runner. The final deployment result is recorded in GitHub Actions and the public release manifest.
