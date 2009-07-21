# coding: utf-8
# Fabfile for Magento deployment
#
# © 2009  Christophe Combelles <ccomb@gorfou.fr>
# This source file is subject to the Open Software License (OSL 3.0)
# that is bundled with this package in the file LICENSE.txt.

# If you want to run commands without setting the user and host from the command
# line, enable the fab_user and fab_hosts variables below. The fab_hosts is a
# list of 'host' or a list of 'user@host'. Examples:
#config.fab_user = 'ccomb'
#config.fab_hosts = ['host']
#config.fab_hosts = ['user@host']
#config.fab_hosts = ['user1@host1', 'user2@host2']

config.wwwdir = '/var/www/site'
config.wwwuser = 'www-data'
config.download_url = \
  'http://www.magentocommerce.com/downloads/assets/$(magento_version)/magento-$(magento_version).tar.gz'

# please keep it in the right order!
patches_urls = """
1.1.8   none
1.2.0.1 http://www.magentocommerce.com/downloads/assets/1.2.0.1/1.1.8-1.2.0.1.diff.tar.gz
1.2.0.2 http://www.magentocommerce.com/downloads/assets/1.2.0.2/1.2.0.1-1.2.0.2.diff
1.2.0.3 http://www.magentocommerce.com/downloads/assets/1.2.0.3/1.2.0.2-1.2.0.3.diff
1.2.1   http://www.magentocommerce.com/downloads/assets/1.2.1/1.2.0.3-1.2.1.diff.tar.gz
1.2.1.1 http://www.magentocommerce.com/downloads/assets/1.2.1.1/1.2.1-1.2.1.1.diff
1.2.1.2 http://www.magentocommerce.com/downloads/assets/1.2.1.2/1.2.1.1-1.2.1.2.diff
1.3.0   http://www.magentocommerce.com/downloads/assets/1.3.0/1.2.1.2-1.3.0.diff
1.3.1   http://www.magentocommerce.com/downloads/assets/1.3.1/1.3.0-1.3.1.diff
""".strip()

config.magento_tarball = config.download_url.split('/')[-1]


def set_host(host):
    """Allows to specify a single target host from the command line
    """
    config.fab_hosts = [host,]

def check():
    """Checks whether we can deploy
    """
    require('fab_hosts')
    require('fab_user')
    local("echo checking needed commands...")
    run('which wget')
    run('which python')
    run('which tar')
    run('which gzip')
    run('which hg')
    run('which sudo')
    run('which chown')
    run('which chmod')
    run('which patch')
    run('which grep')


def prepare_debian():
    """Prepare a Debian/Ubuntu target system for installation
    """
    # check for internet access
    run('ping -c 1 -W 3 peak.telecommunity.com')

    # install required debian packages
    sudo("""
    packages="python python-dev wget tar gzip php5 php5-curl mysql-server"
    aptitude -y install $packages
    """)

    # Reload Apache (if not enough, you must manually restart)
    sudo("/etc/init.d/apache2 reload")

    # install latest Setuptools for Python
    sudo("""
    which easy_install \
        || (wget http://peak.telecommunity.com/dist/ez_setup.py \
            && python ez_setup.py \
            && rm ez_setup.py)
    """)

    # install latest Mercurial
    sudo("which hg || easy_install mercurial")

    # enable the MQ and Graphlog Extensions
    run("""python -c "
import ConfigParser
import os
c = ConfigParser.ConfigParser()
hgrc = os.path.join(os.path.expanduser('~'), '.hgrc')
c.read(hgrc)
c.has_section('extensions') or c.add_section('extensions')
c.has_option('extensions', 'hgext.mq') or c.set('extensions', 'hgext.mq', '')
c.has_option('extensions', 'hgext.graphlog') or c.set('extensions', 'hgext.graphlog', '')
c.write(open(hgrc, 'w'))
    "
    """)



def prepare_redhat():
    """Prepare a Redhat/Fedora/CentOS target system for installation
    """
    # TODO

def wwwdir(path=None):
    """Set the installation path of magento from the fab command line
    """
    if path == None:
        raise EnvironmentError("Please give the wwwdir path "
                               "like in this example: "
                               "wwwdir:/var/www/magento")
    config.wwwdir = path

def wwwuser(user=None):
    """Set the owner of the files from the fab command line
    """
    if user == None:
        raise EnvironmentError("Please give the magento files owner "
                               "like in this example: "
                               "wwwuser:www-data")
    config.wwwuser = user


def get_version():
    """Try to retrieve the installed version
    """
    version = run('grep -A 3 getVersion $(wwwdir)/magento/app/Mage.php | grep return').split("'")[1]
    local('echo Installed version = %s' % version)
    return version


def get_glog():
    """Read the mercurial graphlog
    """
    run('cd $(wwwdir) && hg glog')

def _hgtransaction(decorated_function):
    """Decorator that simulates a transaction using Mercurial.
    It first checks whether everything is commited,
    then do the main job, then commits or reverts everything.
    """
    def new_function(*args):
        # checks for hg and mq
        run('which hg')
        run('hg help qinit > /dev/null')
        # initialize a repo if none
        run('cd $(wwwdir) && [ -e .hg ] || hg init')
        # check there is no uncommited changes
        run('cd $(wwwdir) && [ $(hg st | wc -l) -eq 0 ]')
        # store the possibly applied mq patches
        applied_patches = run('cd $(wwwdir)/magento && hg qapplied')
        print applied_patches
        # unapply all mq patches
        run('cd $(wwwdir)/magento && hg qpop -a')
        try:
            # try to do our main job
            decorated_function(*args)
            # commit the changes
            local('echo Committing changes...')
            run('cd $(wwwdir)/magento && hg addremove')
            run('cd $(wwwdir)/magento && hg ci -m "%s"'
                 % (decorated_function.func_name + unicode(args)))
        except BaseException:
            # rollback
            local('echo Got an error. Reverting all changes...')
            run('cd $(wwwdir)/magento && hg revert -a --no-backup')
        finally:
            try:
                # reapply previously applied patches
                for patch in applied_patches.split('\n'):
                    run('cd $(wwwdir)/magento && hg qpush "%s"' % patch)
            except BaseException:
                local('echo WARNING: Some previously applied patches failed.'
                      'Please fix them manually')

    return new_function


def deploy(version):
    """deploy a magento installation.
    """
    local('echo Deploying version %s' % version)
    check()
    # move previous installation
    sudo('mv $(wwwdir) $(wwwdir).$(fab_timestamp)', fail='warn')

    # create target directory
    sudo("""
    mkdir -p $(wwwdir)/magento
    chown -R $(wwwuser): $(wwwdir)
    chmod -R g+w $(wwwdir)
    """)
    config.magento_version = version
    # download, extract, put under version control
    run("""\
    cd $(wwwdir)/magento
    wget $(download_url)
    tar xzf $(magento_tarball) --strip 1
    rm $(magento_tarball)
    chmod -R g+w .
    cd ..
    echo 'magento/var/cache\nmagento/var/session/\n.*/cache/.*' > .hgignore
    hg init
    hg add
    hg ci -m 'initial magento remote installation version $(magento_version)'
    """)

    # change permissions
    sudo('chgrp -R $(wwwuser) $(wwwdir)')


def savepoint():
    """Create a savepoint after any change in the Magento installation.
    This command creates a new patch with all the uncommited changes and the new
    files, after installing a Magento extension, or patching Magento itself.
    """
    local("echo checking uncommited changes...")
    run('cd $(wwwdir) && [ $(hg st | wc -l) -ne 0 ]')
    run('cd $(wwwdir) && hg qnew -f savepoint-%s' % config.fab_timestamp)
    run('cd $(wwwdir) && hg addremove')
    run('cd $(wwwdir) && hg qrefresh')


@_hgtransaction
def upgrade(to_version):
    """upgrade a magento installation to a higher version.
    """
    from_version = get_version()
    local('echo Wanted version = %s...' % to_version)
    avail_versions = [line.split()[0] for line in patches_urls.split('\n')]
    available_diffs = dict([line.split() for line in patches_urls.split('\n')])
    if from_version not in avail_versions:
        raise ValueError('Upgrading from this version is not supported')
    if to_version not in avail_versions:
        raise ValueError('Upgrading to this version is not supported')
    higher_versions = avail_versions[avail_versions.index(from_version)+1
                                     :avail_versions.index(to_version)+1]
    if len(higher_versions) == 0:
        raise ValueError('Nothing to upgrade')

    for version in higher_versions:
        local('echo Upgrading to version %s...' % version)
        run('cd $(wwwdir)/magento && wget -c %s' % available_diffs[version])
        patch_name = available_diffs[version].split('/')[-1]
        if patch_name.endswith('.tar.gz'):
            run('cd $(wwwdir)/magento && tar xzf %s' % patch_name)
            patch_name = patch_name[:-7]
        try:
            run('cd $(wwwdir)/magento && patch -s -p0 < %s' % patch_name, fail='warn')
            # really stop if there are reject files
            run("cd $(wwwdir) && [ $(find . -name '*.rej' | wc -l) -eq 0 ]")
        finally:
            run('rm $(wwwdir)/magento/%s' % patch_name)







