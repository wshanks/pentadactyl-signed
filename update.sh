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

# Modify install.rdf to change id and update URL
sed -e 's/em:id="pentadactyl@dactyl.googlecode.com"/em:id="pentadactyl-signed@willsalmanj.github.com"/' \
	-e 's#\(em:homepageURL.*\)#\1\n        em:updateURL="https://raw.githubusercontent.com/willsalmanj/pentadactyl-signed/master/update.rdf"#' \
	-e 's#\(em:name.*\)#em:name="PentadactylSigned"#' \
	-i pentadactyl/install.rdf

# Build xpi
mkdir -p downloads
rm -r downloads/*
make -C pentadactyl xpi
cd downloads
mv pentadactyl*.xpi pentadactyl.xpi

# Set version string in install.rdf
unzip pentadactyl.xpi install.rdf
sed -i -e 's/em:version=".*"/em:version="'"$version"'"/' install.rdf
# Set max version in some reasonable way
sed -i -e 's/em:maxVersion=".*"/em:maxVersion="46.0"/' install.rdf
zip -u pentadactyl.xpi install.rdf
rm install.rdf

# Sign xpi
signed_xpi="pentadactyl-signed-$version.xpi"
python "${DIR}/amo_xpi_sign.py" -k "$amo_key" -s "$amo_secret" -x pentadactyl.xpi -o "$signed_xpi"

# Update update.rdf file
sed -e 's#<em:updateLink>.*</em:updateLink>#<em:updateLink>'"https://github.com/willsALMANJ/pentadactyl-signed/releases/download/$version/$signed_xpi"'</em:updateLink>#' \
    -e 's#em:version>.*</em#em:version>'"$version"'</em#' \
	-i "${DIR}/update.rdf"

# Push new update.rdf to GitHub
git commit -a -m "$version"
git tag "$version"
git push --tags

# Upload xpi to GitHub as new release
python "${DIR}/github_release.py" --token "$github_token" --user willsALMANJ \
	--repo pentadactyl-signed --version "$version" --file "$signed_xpi" \
	--content-type application/x-xpinstall
