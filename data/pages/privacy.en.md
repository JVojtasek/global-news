# Privacy — the short version

We do not have your data. That is not a slogan but a consequence of how the site
is built: no server that could receive anything, no database that could hold it,
no account for you to log into.

## What is remembered, and where

Four things, all of them in your own browser, in the storage browsers call
localStorage:

- **your reading balance** — how much news you want, how hard you want it to
  land, and any subjects you have muted
- **your interests** — the sections and subjects you picked, including anything
  you ticked under health, and any topic you typed in yourself. Typed topics are
  matched against headlines and summaries inside your own browser; we never see
  the words you typed
- **the place you chose for the weather**
- **whether you prefer the light or the dark version of the page**

None of it is sent to us, because there is nowhere to send it: this is a static
site, a folder of files. Your personal page is assembled by your own browser from
a list of articles identical for every reader, so ranking it tells us nothing
about you. No login, no profile on our side, nothing for us to look at.

That matters most for the health interests. What you tick there is among the most
sensitive things a person can say about themselves, and our answer is
architectural rather than a promise: it stays with you. A ticked box means
"this interests me", never "I have this". We do not treat you as a patient, and
nothing here is medical advice. For that, ask your doctor.

The site sets no cookies of its own. None at all.

Clear your browser data and it is gone, and we have no copy to restore it from. It
also does not follow you to your phone or another browser. You would set it up
again there, which is the honest price of having no accounts.

## What other people see

We would rather name them than let you find them.

- **[GitHub Pages](https://docs.github.com/en/site-policy/privacy-policies/github-privacy-statement)**
  hosts the site. Like any host, it sees the IP address and browser of everyone
  who loads a page, in its server logs.
- **[Open-Meteo](https://open-meteo.com/en/terms)** provides the forecast, air
  quality and pollen, and **[RainViewer](https://www.rainviewer.com/privacy-policy.html)**
  provides the rain radar. Open the weather page and they receive the coordinates
  you searched for. They cannot answer without them.
  If you press "use my location", the browser gives those coordinates to the
  forecast call and to nothing else — we deliberately do not use a service that
  turns coordinates into a place name, because that would mean handing your exact
  position to a further company purely to print a label.
- **[OpenStreetMap](https://www.openstreetmap.org/copyright)** draws the map under
  the radar and unpkg.com delivers the mapping code. Both see your IP, and only on
  that page.
- **Photographs** come from [Wikimedia Commons](https://commons.wikimedia.org/)
  and [Openverse](https://openverse.org/) under free licences. We download them
  at build time and serve them from our own address, so those sites never see you.
  The exception is a republished article, where pictures may still load from the
  original publisher.

## The one-pixel counter

Articles we offer to other outlets for free republication carry a transparent
image, one pixel by one pixel, pointing back at us with the article's name in the
address. Its job is to count how often a republished piece gets read elsewhere. It
sets no cookie, carries no identifier, and holds nothing about the reader. It
appears only in those copies, never on this site.

## How this is written

Parts of this newsroom are automated, drafts are produced with the help of AI,
and everything is measured against a fixed set of editorial rules before it
appears. Sensitive categories never publish without a human first. More on the
[about page](../about/).

## Ask us anything

jarda.vojtasek@centrum.cz

That includes "what do you have on me". The answer is nothing, and we will gladly
explain why.
