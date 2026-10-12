# Nexvion Networks website

Single-page marketing site for Nexvion Networks Private Limited (private cloud VPS hosting, Noida).

- `index.html` – the whole page: markup, styles and the enquiry-form script. No build step; open it in a browser or serve the folder as static files.
- `assets/` – logo marks for the light and dark header, white logo (footer), full-colour logo, favicon PNGs, and the data center photo from the company deck.
- `favicon.ico` – browser tab icon, generated from the logo mark.
- `.htaccess` – Apache config: HTTPS redirect, security headers, compression, caching, and it blocks direct access to this README.

## Things you will want to edit

- **Plan pricing and specs** – the four cards in the `#plans` section. Prices are indicative placeholders and should be confirmed before launch.
- **WhatsApp number** – `WA_NUMBER` at the top of the script, plus the `wa.me` links in the header, contact card and footer.
- **Phone, email and address** – in the `#contact` section and footer.

The sun/moon button in the header switches between light and dark themes and remembers the choice in the visitor's browser; with no choice made, the site follows the device setting.

The enquiry form does not post anywhere. It composes a message from the fields and opens WhatsApp to the support number with that message pre-filled; the visitor presses send in WhatsApp.

## Production deployment

The production site is **https://nexvionnet.com**. Every push or merged pull request to **`main`** runs `.github/workflows/deploy.yml`, tests the publication boundary, packages the site, and publishes it to the existing cPanel/Apache server. Pull requests run validation only. Feature branches cannot publish through the deployment job, including manual workflow runs.

Public files are `index.html`, `.htaccess`, `favicon.ico`, and supported static files inside `assets/`. The packager generates `version.json` containing `VERSION` and the full deployed Git commit. Repository documentation, visiting cards, tests, workflow files, and credentials are not published. Add new website assets under `assets/`; extend the explicit packaging allowlist if a new public directory or page is needed.

For each change, increment the minor version in `VERSION` (for example, `1.1.0` → `1.2.0`). The initial versioned release is **1.1.0**. Browsers revalidate the page and assets so a new deployment is visible on reload.

Run validation locally with Python 3.10 or newer:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/package_site.py --output /tmp/nexvion-preview --revision "$(git rev-parse HEAD)"
python3 -m http.server 8000 --directory /tmp/nexvion-preview
```

Choose a new output directory for each packaging run. The packager refuses an existing output directory to avoid publishing stale files.

### Deployment access

The workflow uses repository Actions secrets `NEXVION_DEPLOY_SSH_KEY` and `NEXVION_DEPLOY_KNOWN_HOSTS`. These contain a dedicated deployment key and the pinned server host identity. Root passwords are not used by CI. The server account `nexvion-deploy` is restricted to write-only rsync into `/home/nexvionnet/public_html`; it cannot open an interactive shell or use SSH forwarding with this key. The cPanel account keeps its existing disabled SSH shell.

The forced SSH command runs `/usr/bin/rrsync -wo -munge /home/nexvionnet/public_html` as the website owner, `nexvionnet`, through a sudoers rule that permits only that exact command and retains `SSH_ORIGINAL_COMMAND` for rsync validation. It grants no root execution or other commands. Published files remain owned by the cPanel account, so deployment works with the document root's standard `750` permissions without granting group write access.

Synchronization preserves the server's `.well-known/`, `.user.ini`, and `php.ini` files. Public site files are replaced after transfer completes, and removed public files are deleted. GitHub serializes production deployments and verifies the public HTML and release manifest against the exact commit. A failed verification marks the run failed; consult its Actions log before retrying. Transfers are delayed per file, not an atomic whole-site switch.

To roll back, revert the unwanted commit on `main`, bump `VERSION` to the next minor release, and push. This runs the same validated deployment. To republish the current production commit without changing files, run **Validate and deploy website** manually on `main` from the Actions tab. The live identity is available at https://nexvionnet.com/version.json.

## Visiting cards

`cards/` holds print-ready visiting cards in the site's styling.

- `shobhit-sharma-visiting-card.html` – self-contained page (fonts, logos and QR embedded). Open it and print at 100% with no margins; each side is one 3.5 × 2 inch page.
- `shobhit-sharma-visiting-card.pdf` – the same two pages, ready for a print shop.
- `shobhit-sharma-card-front.png`, `shobhit-sharma-card-back.png` – 300 dpi renders of each side.
- `sujeet-kumar-visiting-card.html`, `.pdf`, `sujeet-kumar-card-front.png`, `sujeet-kumar-card-back.png` – the same set for Sujeet Kumar, Founder & CTO.

The QR code on each front is a vCard with that person's name, company, title, both mobile numbers, email, head office address and nexvionnet.com. Scanning it offers to save the contact.
