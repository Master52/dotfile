# .bashrc

# If not running interactively, don't do anything
[[ $- != *i* ]] && return

if command -v eza >/dev/null 2>&1; then
    alias ls='eza --icons=auto --color=auto --group-directories-first'
    alias ll='eza --long --icons=auto --color=auto --group-directories-first'
    alias la='eza --all --icons=auto --color=auto --group-directories-first'
else
    alias ls='ls --color=auto'
fi
# Prefer local integrations, including password copies protected from history.
export PATH="$HOME/.local/bin:$PATH"
# Prompt colours follow the terminal palette, including future theme changes.
__desktop_prompt() {
    local prompt_status=$? branch
    __desktop_git_label=''
    if branch=$(git symbolic-ref --quiet --short HEAD 2>/dev/null); then
        __desktop_git_label="   $branch"
    elif branch=$(git rev-parse --short HEAD 2>/dev/null); then
        __desktop_git_label="   $branch"
    fi
    __desktop_status_label=''
    (( prompt_status == 0 )) || __desktop_status_label=" [$prompt_status]"
}
# Keep branch names as parameter values rather than executable prompt text.
PS1='\[\e[32m\]\u\[\e[90m\]@\h  \[\e[36m\] \w\[\e[32m\]${__desktop_git_label}\[\e[31m\]${__desktop_status_label}\[\e[0m\]\n\[\e[32m\]\$\[\e[0m\] '
if [[ ! " ${PROMPT_COMMAND[*]} " == *' __desktop_prompt '* ]]; then
    PROMPT_COMMAND=(__desktop_prompt "${PROMPT_COMMAND[@]}")
fi

alias gc="cd $HOME/.config"
alias gd="cd $HOME/Downloads"
alias gD="cd $HOME/Documents"
alias gp="cd $HOME/Pictures"
alias gs="cd $HOME/.local/bin"
alias gn="cd /mnt/new-volume/"
alias v="vim "
alias vim="nvim "
alias x="xdg-open "
alias csx="cd ~/.config/sxhkd/"
alias vsx="nvim ~/.config/sxhkd/sxhkdrc"
alias vb="nvim ~/.bashrc"

# Default graphical terminal.
export TERMINAL=kitty


# Added by Antigravity CLI installer
export PATH="/home/master/.local/bin:$PATH"
