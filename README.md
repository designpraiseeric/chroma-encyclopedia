# Chroma: Cinematic Color Encyclopedia

An offline reference on color in film (hue psychology, palette structures, narrative devices, auteur signatures, processes, skin and exposure) with Nigerian-context frames and an annotated bibliography. By DesignPraise Studio.

- **Web app (installable, works offline):** https://designpraiseeric.github.io/chroma-encyclopedia/
  - Android (Chrome): menu → *Install app*.
  - iPhone/iPad (Safari): Share → *Add to Home Screen*.
- **Android APK:** see [Releases](../../releases). Download the latest `.apk` on the phone and open it.

All film-reference frames are **AI re-enactments**: the scene's lighting, palette and composition re-staged in a Nigerian setting with original characters. They are not frames from the films; each tile links to the film's real stills on FILMGRAB.

## Layout
- `src/` source page, frames and an optional `stills/` folder for your own frame grabs (named as in the in-app manifest).
- `tools/build.py` builds the offline web app into `www/` (compressed frames, bundled fonts, service worker, manifest).
- `tools/icons.py` regenerates the app icons and splash in `assets/`.
- `.github/workflows/` deploys `www/` to GitHub Pages and builds the Android APK on every push to `main`.

Local build: `npm ci && pip install pillow && npm run build`, then serve `www/` with any static server.
