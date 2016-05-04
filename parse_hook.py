import glob
import json
import logging
import re
import subprocess
import git
import knife

import config


logging.basicConfig(filename='logs/commis.log',level=logging.INFO)

logging.debug('\n\n\n')
logging.info('\n\n\n')

chef_repo_path = config.chef_repo_path
cookbooks_path = config.cookbooks_path

def current_release():
    # TODO get this from a file, which can be created by hand to start with,
    # then modified automatically when a new release is created
    # May also need to be a lookup between sequential/numerical release and nonlinear-named release
    return "2016.3"

def env_to_version_lookup(env_name):
    # TODO get this from a file, which can be created by hand to start with,
    # then modified automatically when a new env is added
    table = {"york":    "1",
             "paris":   "2",
             "sf":      "3",
             "staging": "4",}
    return table[env_name]

def version_for(release, env_name):
    return release+"."+env_to_version_lookup(env_name)

def get_branch_from_push(hook_data):
    ref = hook_data['ref']
    branch = ref.split("refs/heads/")[-1]
    return branch

def get_env_from_push(hook_data):
    ref = hook_data['ref']
    branch = get_branch_from_push(hook_data)
    if "develop" in branch or "master" in branch:
        # print "You have pushed to a non-environment branch. Chef will not be updated with your changes."
        return branch
    if "env" in branch:
        env = branch.replace("env/","")
    print "Environment is "+env
    return env

def get_files_changed_by_push(hook_data):
    # Get list of files modified and/or added
    modified = [commit.get('modified') for commit in hook_data.get('commits')]
    added = [commit.get('added') for commit in hook_data.get('commits')]
    changed = modified + added  # add both lists of files
    changed = [item for sublist in changed for item in sublist]  # flatten
    logging.info("The following files were changed: " + str(changed))
    return changed

def get_knife_cmd_from_filepath(filepath):
    path_to_knife= {"environments": "environment from file ",
                    "cookbooks": "cookbook upload ",
                    "site-cookbooks": "cookbook upload ",
                    "nodes": "node from file "}
    resource_type = filepath.split("/")[0]
    knife_cmd = "knife " + path_to_knife[resource_type]
    knife_path = filepath.split("/")[1] if "from file" not in knife_cmd else filepath
    command = knife_cmd + knife_path
    return command

def get_knife_changes_for_push(hook_data):
    changed_files = set(get_files_changed_by_push(hook_data))

    def reject_wrong_envs(filepath):
        if not filepath.startswith("environments"):
            return True
        branch = get_branch_from_push(hook_data).split("/")[-1]
        env = filepath.split("/")[-1].split(".rb")[0]
        if env == branch:
            return True
        print "Warning: " + filepath + " is an environment file which does not match this env branch"
        print "Knife will ignore this change"
        return False

    print changed_files
    changed_files = filter(reject_wrong_envs, changed_files)
    print changed_files
    knife_changes = list(set([get_knife_cmd_from_filepath(f) for f in changed_files]))
    return knife_changes




def get_all_metadata_file_paths():
    md_files = glob.glob(cookbooks_path+"/*/metadata.rb")
    return md_files

def set_version_in_metadata_file(md_path, new_version):
    # print md_path.split("/")[-1]
    cmd = "grep version " + md_path
    old_version_line = subprocess.check_output(cmd.split()).strip()
    # print "old version line: "+old_version_line+"/n"
    re_triparte = "\d+\.\d+\.\d+"
    old_version = re.findall(re_triparte, old_version_line)[0]
    # print old_version
    logging.debug("md_path: {}, old_version: {}".format(md_path, old_version_line))
    new_version_line = old_version_line.replace(old_version, new_version)
    # print "new version line: "+new_version_line+"/n"
    cmd = "sed@-i@.bak@s/{old_str}/{new_str}/g@{md_path}".format(old_str=old_version_line, new_str=new_version_line, md_path=md_path)
    # print "cmd: "+cmd+"/n"
    logging.debug(cmd)
    # print(cmd)
    subprocess.check_output(cmd.split("@"))
    return

def set_version_in_all_metadata_files(new_version):
    md_paths = get_all_metadata_file_paths()
    num_md_files = len(md_paths)
    print "Setting all {} cookbook metadata files to version {}".format(num_md_files, new_version)
    for md in md_paths:
        set_version_in_metadata_file(md, new_version)



def update_repo_to_commit(hook_data):
    commit_hash = hook_data['after']
    git.pull(commit_hash)
    branch = get_branch_from_push(hook_data)
    git.checkout(branch)
    return

def handle_push(hook_data):
    update_repo_to_commit(hook_data)
    branch = get_env_from_push(hook_data)
    if "develop" in branch or "master" in branch:
        print "Push to non-environment branch, no Chef changes to make"
        return
    env_version = version_for(current_release(), branch)
    set_version_in_all_metadata_files(env_version)
    knife_commands = get_knife_changes_for_push(hook_data)
    print "Running the following knife commands:"
    for k_cmd in knife_commands:
        knife.run(k_cmd)
    # Todo determine when to do this and add knife env file to k_cmds
    set_cookbook_versions_in_env_file(branch, env_version)


def set_cookbook_versions_in_env_file(env, new_version):
    env_file_path = "{}/environments/{}.rb".format(chef_repo_path, env)
    logging.info("setting cookbook versions in env file {}".format(env_file_path))
    with open(env_file_path, "r") as env_file:
        old_env_text = "".join(env_file.readlines())
    # extract site-cookbooks from text into usable list
    raw_versions = re.compile('# site-cookbooks\n(.*)?\}\)', re.DOTALL).findall(old_env_text)[0]
    site_cookbooks_list = re.compile('"(.*)?" =>').findall(raw_versions)
    logging.info("found the following site-cookbooks: {}".format(str(site_cookbooks_list)))
    # Recreate the site-cookbooks section with new versions
    new_sc_versions = ",\n".join(['  "{}" => "= {}"'.format(sc, new_version) for sc in site_cookbooks_list])
    # print new_sc_versions
    new_sc_versions = "# site-cookbooks\n" + new_sc_versions + "\n})"
    # paste the new version info into the original file
    new_env_text = re.compile('# site-cookbooks\n.*?\}\)', re.DOTALL).sub(new_sc_versions, old_env_text)
    print new_env_text
    with open(env_file_path, "w") as env_file:
        env_file.write(new_env_text)


if __name__ == "__main__":
    # Get the example githook data
    with open("tests/hook_data.json", "r") as data_file:
        data1 = json.load(data_file)

    # Get the example githook data
    with open("tests/hook_data2.json", "r") as data_file:
        data2 = json.load(data_file)
    handle_push(data1)
    handle_push(data2)
    # set_cookbook_versions_in_env_file("paris", "12.34.56")
