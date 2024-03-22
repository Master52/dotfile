

export NNN_PLUG='f:finder;o:fzopen;p:preview-tui;d:diffs;t:nmount;v:preview-tabbed;n:nuke'
export NNN_FIFO="/tmp/nnn.fifo"
export NNN_OPENER="/home/master/.config/nnn/plugins/nuke"
export NNN_TERMINAL="kitty"


ZINIT_HOME="${XDG_DATA_HOME:-${HOME}/.local/share}/zinit/zinit.git"
[ ! -d $ZINIT_HOME ] && mkdir -p "$(dirname $ZINIT_HOME)"
[ ! -d $ZINIT_HOME/.git ] && git clone https://github.com/zdharma-continuum/zinit.git "$ZINIT_HOME"
source "${ZINIT_HOME}/zinit.zsh"

# Use powerline
USE_POWERLINE="true"
# Has weird character width
# Example:
#    is not a diamond
HAS_WIDECHARS="false"
# Source manjaro-zsh-configuration
if [[ -e /usr/share/zsh/manjaro-zsh-config ]]; then
  source /usr/share/zsh/manjaro-zsh-config
fi
# Use manjaro zsh prompt
if [[ -e /usr/share/zsh/manjaro-zsh-prompt ]]; then
  source /usr/share/zsh/manjaro-zsh-prompt
fi


export LC_ALL=en_US.UTF8
export FZF_DEFAULT_OPTS="--preview 'bat --color=always {}'"

# zsh-fzf-history-search
plugins=(… zsh-fzf-history-search)
zinit ice lucid wait'0'
zinit light joshskidmore/zsh-fzf-history-search


# Linux version of OSX pbcopy and pbpaste.
alias pbcopy="xsel --clipboard --input"
alias pbpaste="xsel --clipboard --output"
alias ls="exa -l  --color=auto"
alias l="exa -al"

alias cv="vim ~/.vim/vimrc"
alias v="vim"
alias vdwm="vim ~/dwm-6.3/config.h"
alias cdwm="cd ~/dwm-6.3/ && l"
alias csc="cd ~/scripts/ && l"
alias cD="cd ~/Downloads/ && l"
alias cP="cd ~/Pictures/ && l"
alias vz="vim ~/.zshrc"
alias ss="cd ~/scripts/"
vf() { vim $(find $1 -type f | fzf )}
cdf() { cd $(find $1 -type d | fzf )}
alias yt="ytfzf -t"
alias q="exit"
alias n="nnn -P p"
alias cdp="cd \$(find /mnt/master/projects  -maxdepth 1 | fzf)"
alias cdw="cd \$(find /mnt/master/websites  -maxdepth 1 | fzf)"
alias cdd="cd \$(find ~/dotfiles  -maxdepth 2 | fzf)"
alias cddr="cd \$(find /mnt/master  -maxdepth 1 | fzf)"


set -o vi




