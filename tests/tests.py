import unittest
import parse_hook
from random import randint


class HookParseTest(unittest.TestCase):
    def testKnifeCmd(self):
        data = [("environments/york.rb", "knife environment from file environments/york.rb"),
                ("nodes/paris/web.rb", "knife node from file nodes/paris/web.rb"),
                ("cookbooks/nginx/recipes/default.rb", "knife cookbook upload nginx"),
                ("site-cookbooks/mysql/files/default/ssl.crt", "knife cookbook upload mysql"),]
        for test, result in data:
            self.assertEqual(parse_hook.get_knife_cmd_from_filepath(test), result)

    def testSetMetadata(self):
        md_path = "/Users/davidwalker/workspace/branch_chef/chef-demo/cookbooks/SDP/metadata.rb"
        new_version = "12.345."+str(randint(0,100))
        parse_hook.set_version_in_metadata_file(md_path, new_version)
