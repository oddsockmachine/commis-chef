import re
import subprocess

def get_version_from_metadata(metadata_file_path):
    chef_home = "~/workspace/branch_chef/chef-repo/"
    subprocess.check_call(["ls", "-l", "../chef-repo"])

get_version_from_metadata("x")
