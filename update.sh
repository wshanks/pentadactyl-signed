#!/usr/bin/env bash

#  This file is part of pentadactyl-signed
#
# pentadactyl-signed is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# pentadactyl-signed is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2016, willsALMANJ

set -e

# Must run from directory containing script file
OS="$(uname)"
if [ $OS = "Linux" ] ; then
	DIR="$( cd -P "$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")" && pwd)"
elif [ $OS = "Darwin" ] ; then
	FILEPATH=$(readlink "${BASH_SOURCE[0]}")
	# Check exit status of readlink -- nonzero means BASH_SOURCE not a symlink
	if [ $? != 0 ] ; then
		FILEPATH="${BASH_SOURCE[0]}"
	fi
	DIR="$( cd -P "$(dirname "${FILEPATH}")" && pwd)"
fi
cd "$DIR"


# Set up variables
last_version="$(git tag -l --sort=v:refname | tail -1)"
amo_secret="$(cat amo.secret)"
amo_key="$(cat amo.key)"
github_token="$(cat github.token)"
addon_id="$(cat addon_id.txt)"
github_user="$(cat github_user.txt)"
github_repo="$(cat github_repo.txt)"

# Update dactyl source
cd dactyl
hg revert --all
hg pull
hg update

# Get version number and exit if no changes
version="$(hg log -r . --template '{rev}')"
if [ "$last_version" = "$version" ]; then
	exit 0
fi

# Get max Firefox version
max_fx_version="$(python "${DIR}"/max_firefox_version.py)"

# Modify install.rdf to change id, update URL, and max Firefox version
sed -e 's/em:id="pentadactyl@dactyl.googlecode.com"/em:id="'"$addon_id"'"/' \
	-e 's#\(em:homepageURL.*\)#\1\n        em:updateURL="https://raw.githubusercontent.com/'"$github_user"'/'"github_repo"'/master/update.rdf"#' \
	-e 's#\(em:name.*\)#em:name="PentadactylSigned"#' \
     -e 's/em:maxVersion=".*"/em:maxVersion="'"$max_fx_version"'"/' \
	-i pentadactyl/install.rdf

# Build xpi
mkdir -p downloads
# rm -rf downloads/*
# make -C pentadactyl xpi
cd downloads
# mv pentadactyl*.xpi pentadactyl.xpi

# Set version string in install.rdf
unzip pentadactyl.xpi install.rdf
sed -i -e 's/em:version=".*"/em:version="'"$version"'"/' install.rdf
zip -u pentadactyl.xpi install.rdf
rm install.rdf

# Sign xpi with jpm
# Python wrapper makes sure the signed xpi file ends up at a known location
signed_xpi="pentadactyl-signed-$version.xpi"
# python "${DIR}/amo_xpi_sign.py" -k "$amo_key" -s "$amo_secret" -x pentadactyl.xpi -o "$signed_xpi"

# Update update.rdf file
sed -e 's#<em:updateLink>.*</em:updateLink>#<em:updateLink>'"https://github.com/'"$github_user"'/'"$github_repo"'/releases/download/$version/$signed_xpi"'</em:updateLink>#' \
    -e 's#em:version>.*</em#em:version>'"$version"'</em#' \
    -e 's#em:maxVersion>.*</em#em:maxVersion>'"$max_fx_version"'</em#' \
	-i "${DIR}/update.rdf"

# Push new update.rdf to GitHub
git commit -a -m "$version"
git tag "$version"
git push --tags

# Upload xpi to GitHub as new release
python "${DIR}/github_release.py" --token "$github_token" --user "$github_user" \
	--repo "$github_repo" --version "$version" --file "$signed_xpi" \
	--content-type application/x-xpinstall
