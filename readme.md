# Pentadactyl signing scripts
---
These scripts download the latest Pentadactyl commit, build the xpi, sign
the xpi with Mozilla's signing API, and then upload the xpi to GitHub as a new
release.

It is not possible for anyone else to run them as is because they are
hard-coded to update this repo and a specific addon id used for Pentadactyl on
Mozilla's servers, but the scripts could be modified to be used by someone
else. For this reason, a brief description of the set up is given below.

## External dependencies
Scripts require `bash` and `python` (version 3) as well as these Python
packages:
* beautifulsoup4
* lxml
* PyJWT
* requests
* requests-jwt

## Setup
* The scripts assume that files `github.token`, `amo.key`, and `amo.secret` are
  in the working directory.

* An existing GitHub repo is needed to push the xpi files to for release.

* The scripts assume that main Pentadactyl repo on GitHub has already been
  cloned to the `dactyl` directory as an `mercurial` repo using `hg-git`.

## TODO
* Encapsulate repo specific references, so anyone else could easily fork this
  and run their own version.

* Pull the maximum Firefox version from the internet and udpate `install.rdf`
  and `update.rdf` with it.
