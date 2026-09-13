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
