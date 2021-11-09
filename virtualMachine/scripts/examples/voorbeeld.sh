#!/bin/bash

# abort on nonzero exitstatus
# set -o errexit
# abort on unbound variable
set -o nounset
# don't hide errors within pipes
set -o pipefail

readonly HELLO="Hello"
#myvar=`pwd`
myvar=$(pwd)

log(){
    printf "%s" $1
}

main(){
     set -x
    local message1=$1
    local message2=$2
    local statement=$3
    unset -x
   
    if [[ "${statement}" == "1" ]]; then
        log "${message1} ${USERNAME}"
    else
        log "${message2} ${USERNAME}"
    fi
}

main "${@}"
