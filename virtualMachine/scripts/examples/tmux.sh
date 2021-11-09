#!/bin/bash
tmux new-session -d
ssh_list=( lab002_centos.vs-lab.local lab002_ubuntu.vs-lab.local lab002_centos.vs-lab.local lab002_ubuntu.vs-lab.local )

split_list=()
for ssh_entry in "${ssh_list[@]:1}"; do
    split_list+=( split-pane ssh "$ssh_entry" ';' )
done

tmux new-session ssh "${ssh_list[0]}"';' \
    "${split_list[@]}" \
    select-layout tiled ';' \
    set-option -w synchronize-panes

