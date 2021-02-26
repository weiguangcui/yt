import os
import unittest

import yt
from yt.config import CONFIG_DIR, ytcfg
from yt.testing import assert_raises, fake_random_ds

TEST_PLUGIN_FILE = """
import numpy as np

def _myfunc(field, data):
    return np.random.random(data['density'].shape)
add_field('random', dimensions='dimensionless',
          function=_myfunc, units='auto', sampling_type='local')
constant = 3
def myfunc():
    return constant*4
foobar = 17
"""


def setUpModule():
    my_plugin_name = ytcfg.get("yt", "plugin_filename")
    # In the following order if plugin_filename is: an absolute path, located in
    # the CONFIG_DIR, located in an obsolete config dir.
    old_config_dir = os.path.join(os.path.expanduser("~"), ".yt")
    for base_prefix in ("", CONFIG_DIR, old_config_dir):
        potential_plugin_file = os.path.join(base_prefix, my_plugin_name)
        if os.path.isfile(potential_plugin_file):
            os.rename(potential_plugin_file, potential_plugin_file + ".bak_test")

    plugin_file = os.path.join(CONFIG_DIR, my_plugin_name)
    with open(plugin_file, "w") as fh:
        fh.write(TEST_PLUGIN_FILE)


def tearDownModule():
    from yt.fields.my_plugin_fields import my_plugins_fields

    my_plugins_fields.clear()
    my_plugin_name = ytcfg.get("yt", "plugin_filename")
    plugin_file = os.path.join(CONFIG_DIR, my_plugin_name)
    os.remove(plugin_file)


class TestPluginFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        my_plugin_name = ytcfg.get("yt", "plugin_filename")
        # In the following order if plugin_filename is: an absolute path, located in
        # the CONFIG_DIR, located in an obsolete config dir.
        old_config_dir = os.path.join(os.path.expanduser("~"), ".yt")
        for base_prefix in ("", CONFIG_DIR, old_config_dir):
            potential_plugin_file = os.path.join(base_prefix, my_plugin_name)
            if os.path.isfile(potential_plugin_file):
                os.rename(potential_plugin_file, potential_plugin_file + ".bak_test")

        plugin_file = os.path.join(CONFIG_DIR, my_plugin_name)
        with open(plugin_file, "w") as fh:
            fh.write(TEST_PLUGIN_FILE)

    @classmethod
    def tearDownClass(cls):
        my_plugin_name = ytcfg.get("yt", "plugin_filename")
        plugin_file = os.path.join(CONFIG_DIR, my_plugin_name)
        os.remove(plugin_file)

        old_config_dir = os.path.join(os.path.expanduser("~"), ".yt")
        for base_prefix in ("", CONFIG_DIR, old_config_dir):
            potential_plugin_file = os.path.join(base_prefix, my_plugin_name)
            if os.path.isfile(potential_plugin_file + ".bak_test"):
                os.rename(potential_plugin_file + ".bak_test", potential_plugin_file)
        del yt.myfunc

    def testCustomField(self):
        plugin_file = os.path.join(CONFIG_DIR, ytcfg.get("yt", "plugin_filename"))
        msg = f"INFO:yt:Loading plugins from {plugin_file}"

        with self.assertLogs("yt", level="INFO") as cm:
            yt.enable_plugins()
            self.assertEqual(cm.output, [msg])

        ds = fake_random_ds(16)
        dd = ds.all_data()
        self.assertEqual(str(dd[("gas", "random")].units), "dimensionless")
        self.assertEqual(dd[("gas", "random")].shape, dd[("gas", "density")].shape)
        assert yt.myfunc() == 12
        assert_raises(AttributeError, getattr, yt, "foobar")
