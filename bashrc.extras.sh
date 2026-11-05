# shellcheck shell=bash
# Additions to .bashrc
# Add to your .bashrc: source unix_stuff/bashrc.extras.sh

export LESS=-XFR
export EDITOR=emacs

# "Darwin" is OS X
# TODO: check for any BSD flavor
if [[ $(uname) == "Darwin" ]]; then
    export LESS=-XIr
    alias ls="ls -FG"
    # See https://www.emacswiki.org/emacs/EmacsForMacOS#h5o-25
    export EDITOR="/Applications/Emacs.app/Contents/MacOS/Emacs"
    alias emacs='$EDITOR'
fi

# Remove all containers that have exited
alias docker-rm-exited='docker rm $(docker ps -q -f status=exited)'

if [[ -r ~/.django_bash_completion.sh ]]; then
   # Lives outside this repo, so shellcheck can't follow it.
   # shellcheck source=/dev/null
   source ~/.django_bash_completion.sh
fi


# takes output of uniq -c and produces a tsv
uniqtsv() {
    perl -lpe 's/^\s*(\d+)\s+(.*)/$1\t$2/' "$@"
}
