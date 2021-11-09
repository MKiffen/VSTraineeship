#! /usr/bin/env bash
#
# Author: Dennis in 't Groen <dgroen@virtualsciences.nl>
#
#/ Usage: SCRIPTNAME [OPTIONS]... [ARGUMENTS]...
#/
#/
usage="$(basename "$0") [OPTIONS]... [VAGRANT OPTIONS]... [VAGRANT ARGUMENTS]....
Commandline helper script for custom Vagrantfile implementations.

OPTIONS

-h, --help
Print this help message

*** Required ***
-bc [filename], --boxes-config [filename]"

#/
#/ EXAMPLES
#/
 
 
#{{{ Bash settings
# abort on nonzero exitstatus
set -o errexit
# abort on unbound variable
set -o nounset
# don't hide errors within pipes
set -o pipefail
#}}}
#{{{ Variables
readonly script_name=$(basename "${0}")
readonly script_dir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
IFS=$'\t\n' # Split on newlines and tabs (but not on spaces)
 
#}}}
 
main() {
# check_args "${@}"

}
 
#{{{ Helper functions
 show_help(){
    printf '%b\n' ""
    printf '%b\n' "${usage}" | less -g
    exit
}

 
 
#}}}
 
main "${@}"
 
# cursor: 33 del