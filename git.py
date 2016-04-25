import logging
from time import sleep

def get_commit(hook_data):
    commit_hash = hook_data['after']
    cmd = "git pull "+commit_hash
    print cmd
    sleep(1)
    branch = get_branch_from_push(hook_data)
    cmd = "git checkout " + branch
    print cmd
    sleep(1)
    return

def pull(commit_hash):
    cmd = "git pull " + commit_hash
    print cmd
    sleep(1)
    return

def checkout(branch):
    cmd = "git checkout " + branch
    print cmd
    sleep(1)
    return
