# Pentadactyl signing scripts
---
These scripts download the latest Pentadactyl commit, build the xpi, sign
the xpi with Mozilla's signing API, and then upload the xpi to GitHub as a new
release.

## Using the `.xpi` files
The `.xpi` files are available in the releases section of the repo on GitHub.
The signing/publishing script sets the update URL for the addon to point at the
`update.rdf` file in the repo, so every time a new `.xpi` is published to the
repo Firefox should automatically pull down this update if automatic updates
are enabled.

## Signing and publishing your own `.xpi` files
### External dependencies
Scripts require `bash`, `python` (version 3.5 or greater), and `jpm` (version
1.0.5 or greater) as well as these Python packages:
* beautifulsoup4
* requests
* uritemplate

### Setup
* A user account on (addons.mozilla.org) and GitHub account and new GitHub repo
  are needed to sign and publish the `.xpi` files.

* The scripts assume the following text files are present in the top level of
  the repo:

  - `github.token`: Contains a GitHub authentication token string that can be
    generated from a GitHub account's profile page for working with the GitHub
API

  - `amo.key`: Contains the user account key for working with the
    (addons.mozilla.org) API.

  - `amo.secret`: Contains the authentication secret for working with the
    (addons.mozilla.org) API.

  - `addon_id.txt`: Contains the addon id used for the Pentadactyl `.xpi` file.
    This must be unique across all Mozilla addons and must be associated with
your (addons.mozilla.org) account used for signing (if you choose a unique and
sign it once that is enough to associate it with your account).

  - `github_user.txt`: User account name on GitHub

  - `github_repo.txt`: Name of the repo on GitHub used for publishin the `.xpi`
    files.

* The [main Pentadactyl repo on GitHub](https://github.com/5digits/dactyl) has
  already been cloned to a directory named `dactyl` inside the root of this git
repo. This repo should be cloned using `hg-git` as a `mercurial` repo (it is
cloned in this way so that the `mercurial` revision number can be used as the
version number as is done with the main Pentadactyl repo, though for some
reason, probably related to the translation from `hg` to `git` and back to
`hg`, the numbers don't match exactly).

### Running the script
All that should be needed is to run the `update.sh` bash script. The script
takes the following steps:

* Pull  the latest commits from the main Pentadactyl repo

* Compare the latest Pentadactyl revision number against the last published
  revision number (published revision numbers are stored as tags in the `git`
repo). Stop if there are no new Pentadactyl revisions.

* Update `install.rdf` with a new addon id, a valid maximum Firefox version
  string (the one in the Pentadactyl repo was rejected by the
(addons.mozilla.org) signing API, and a new update URL (pointing at the GitHub
repo).

* Build the `.xpi` file

* Update `install.rdf` again to set the version string (it gets set in the
  build process).

* Sign the `.xpi` file

* Update `update.rdf` to point at the new version number

* Commit the update to `update.rdf`, tag the commit with the new version
  number, and push it to GitHub

* Upload the `.xpi` file to GitHub as a release file associated with the new
  tag
