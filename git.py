import logging
import subprocess
from time import sleep

def git(cmd):
    print cmd
    g = "git -C /opt/chef-repo/ "
    cmd = g + cmd
    # print subprocess.check_output(cmd.split(" "))

def get_commit(hook_data):
    commit_hash = hook_data['after']
    git("pull "+commit_hash)
    sleep(1)
    branch = get_branch_from_push(hook_data)
    git("checkout " + branch)
    sleep(1)
    return

def pull(commit_hash):
    git("pull " + commit_hash)
    sleep(1)
    return

def checkout(branch):
    git("checkout " + branch)
    sleep(1)
    return
