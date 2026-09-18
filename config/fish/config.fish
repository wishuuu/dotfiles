if status is-interactive
    set -g fish_greeting
    if command -q fzf
        fzf --fish | source
    end
    if command -q direnv
        direnv hook fish | source
    end
end
# Narzędzia rustup instalowane osobno dla użytkownika.
fish_add_path $HOME/.cargo/bin
