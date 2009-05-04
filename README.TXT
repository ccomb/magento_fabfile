=========================================================
Professional Magento deployment with Fabric and Mercurial
=========================================================

.. highlights::

  | Author : Christophe Combelles <ccomb@gorfou.fr>
  | for Emencia http://emencia.com

.. contents::


Warning
=======
This article and the provided fabfile are just a food for thought and need to be discussed!
Feedback appreciated.

Quickstart
==========
If you are in a hurry, if you already know Magento, Mercurial, MQ Extension and Fabric and
you don't like to read documentation, here is a quickstart for Debian or Ubuntu.

Install the required tools on your machine::

  $ sudo aptitude install python2.5 python-setuptools
  $ sudo easy_install fabric==0.1.1
  $ wget https://cody.gorfou.fr/hg/magento_fabfile/raw-file/tip/fabfile.py

Prepare a Debian server for deployment:

  $ fab set_host:user@host prepare_debian

Deploy Magento 1.2.1:

  $ fab set_host:user@host deploy:1.2.1

Upgrade Magento to 1.3.1:

  $ fab set_host:user@host upgrade:1.3.1

Check installed version:

  $ fab set_host:user@host get_version

Professional means safe and quick. The core idea is to deploy Magento on the
server into a *Mercurial* repository, so that everything is versioned, and
to use *Fabric* to automate the deployment, the upgrade, and the patches
management.  The main Mercurial history is used for upgrades, and MQ patches are
used for extensions and customization.  During an upgrade, all patches are
unapplied, diffs are applied, then patches are reapplied. Mercurial is used to
simulate a transactional system, so if an upgrade fails, everything is safely
reverted to the previous state.

Everything is done using a single fabfile. The fabfile defines useful commands
for deployment or upgrades. The actual Mercurial commands are defined in the
fabfile. As a result, deployments and upgrades should be feasible without any
Python, Fabric or Mercurial knowledge.

Note that such a deployment leads to the exact same result as a manual
deployment. The only difference will be a ``.hg`` directory containing the
Mercurial repository. This directory is located one level higher than the
Magento installation, so it is not exposed to the web (provided your Apache
virtualhost points to the Magento directory).


Introductions and prerequisites
===============================

Magento
~~~~~~~
Magento is an eCommerce platform written in PHP. It allows you to create online
shops quickly and easily, with unprecedented flexibility and excellent usability.
Like almost any other PHP application, it can be installed very
easily, with two different methods:

 * download the full Magento archive, extract it on your hard disk, then upload all the files
   onto your server by FTP. Or,

 * download a small downloader package, extract it on your hard disk, upload all
   the files onto your server by FTP, then access the downloader through your
   browser and let it finish downloading and installing the remaining files.

That's the common way of installing Magento on a shared hosting. If you own a
dedicated or private server, the method is exactly the same, except that you do
everything directly from the shell on your server.

Easy? Yes, if you install a single Magento instance. As soon as you are a web
agency or integrator, and if you deploy, customize, upgrade and maintain a bunch
of Magento instances, you will loose a lot of time, and possibly do errors. You
probably won't be able to safely upgrade a heavily customized (or even manually
patched) installation of Magento.  Worst of all, you won't be able to *know*
what has been done on a particular instance, unless you (and all your staff) are
very well organized. But you are, aren't you? ;-)

If you do professional Magento deployment, you definitely want to:

 * Quickly deploy without manually downloading, uploading, chmod'ing, etc.

 * Immediately put the installation under version control, to keep a full history
   of all the upgrades and customizations

 * Be able to remotely upgrade Magento with diff files provided by *Varien* (the company
   that distributes and maintains the Magento source code)

 * Be able to apply diffs, **even** if you heavily modified the Magento source code, or
   if you have a lot of installed extensions.

 * Instantly (and remotely) know which version is installed

 * Be able to deploy again a custom Magento installation, with custom skins,
   custom extensions, custom patches, etc.


To be able to achieve all these tasks, we will use three very good tools:

 * Fabric ( http://www.nongnu.org/fab/ )

 * Mercurial ( http://www.selenic.com/mercurial )

 * Mercurial MQ Extension ( http://www.selenic.com/mercurial/wiki/index.cgi/MqExtension )


Fabric
~~~~~~

Fabric is a simple tool that allows you to run remote commands on several
servers, upload files on these servers, and automate things by creating simple
commands.

For instance, we will be able to deploy Magento 1.3.0 with a single command line like
this:

$ fab deploy:1.3.0

Installation
------------
Fabric is needed on your machine, not on the server.

To install Fabric, you first need to install Python, since Fabric is written in
Python. If you use a Debian or Ubuntu system, just run the following commands as
root (or prepend ``sudo`` if you're not root but sudoer)::

  # aptitude install python2.5 python-setuptools
  # easy_install fabric==0.1.1

If you're using MacOs or Windows, the steps are similar: first, check you have
Python 2.5, then easy_install fabric. Note that I have no idea whether Fabric
works on Windows or not.

You should now have a``fa`` shell command available. If you run it without arguments, you will
discover which commands are available. If your current shell directory contains a
``fabfile.py`` file, additional commands are available.

Documentation
-------------

 * Currently here: http://www.nongnu.org/fab/documentation.html
 * Soon here: http://fabfile.org

Mercurial
~~~~~~~~~
Mercurial is a very fast, easy-to-use and well-known Distributed Version Control
System, used by large projects such as Mozilla, OpenJDK, OpenSolaris or Python.
If you already use Subversion, you will be able to use Mercurial in a matter of
minutes. The main conceptual difference is that every *checkout* is also a full
repository. So it is called a *clone* instead of a *checkout*, and you do
check-ins locally. Mercurial is much more powerful than Subversion for branching
and merging, and comes with a lot of interesting plugins. It also avoids
maintaining a central repository. When you want to version-control a new project
or directory, just run ``hg init`` and that's all.  Then you can start adding
files in the repository and commit changes offline.  You will be able to
synchronize your repository with another one, locally or remotely.

Installation
------------
Mercurial is needed on the server, not on your machine.

Recent Linux systems already offer a Mercurial package. On Debian or Ubuntu, just
run the following command as root (or sudo) on your server:

  # aptitude install mercurial

If you want a more recent version or if Mercurial is not already packaged,
install it with easy_install:

  # easy_install mercurial

MQ Extension
------------
Now you should enable the MQ Extension. This extension offers patch management,
just like *quilt* does, but integrated with Mercurial. It will be used for
Magento extensions and customizations.

To enable the MQ Mercurial extension on the server, add the following line in the
[extensions] section of your .hgrc.:

  hgext.mq =

You can check whether MQ is enabled by running: ``hg help qinit``

The Fabfile
===========

After installing *Fabric* on your machine and *Mercurial/MQ* on the server, all you
need to do is download the *fabfile*. You can get the latest version here:

https://cody.gorfou.fr/hg/magento_fabfile/raw-file/tip/fabfile.py

When you run the ``fab`` shell command, Fabric will look for a ``fabfile.py`` in
the current directory. All the fabric commands defined in the fabfile will be
instantly available to Fabric. After downloading the ``fabfile.py``, go to the
directory containing this file, and run: ``fab``. You should see some specific
commands, such as ``deploy``, ``upgrade`` or ``get_version``.

Configuration
~~~~~~~~~~~~~
You need to adapt some parameters to your environment. Open the fabfile
and look at the first few variables defined at the top of the file:

 * ``config.wwwdir`` is the target directory in the server. You should replace
   '/var/www/site' with the intended DocumentRoot of your Magento site.

 * ``config.wwwuser`` is the system user that will own all the files in the
   Magento installation. The typical value for a Debian system is 'www-data'.

Check the server environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Make sure your server can be accessed through SSH.
To check if the server is ready for a Magento deployment, run:

  $ fab check

Anyway, this command will automatically be run before any other command. It
checks whether required tools are available, such as *wget*, *python*, *mercurial*, etc.

Preparing the server for deployment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
In order to be able to run Magento, your server should offer several required
tools, such as PHP5 or MySQL, and tools used for deployments and upgrades, such
as *Mercurial*, *wget* or *patch*.

If you want to prepare a Debian/Ubuntu server for deployment, run:

  $ fab set_host:user@host prepare_debian

If you want to see what it does, just look at the corresponding command in the
fabfile.

Deploy Magento
~~~~~~~~~~~~~~
Now that your server is ready for deployment, you can deploy Magento 1.2.1 with:

  $ fab set_host:user@host deploy:1.2.1

``set_host:user@host`` is a required command if you did not set the fab_host
config variable at the beginning of the fabfile. Use it to set the user and host
for deployment. Note that the user should be sudoer on the server.

If you deploy twice, the previous site is not overwritten, but renamed with a
timestamp.


Check Magento version
~~~~~~~~~~~~~~~~~~~~~
To retrieve the version number of the deployed Magento instance, run:

  $ fab set_host:user@host get_version


Customize Magento
~~~~~~~~~~~~~~~~~
After installing a Magento extension, you can create a savepoint to your
repository. The savepoint is created as an MQ patch, so it can be unapplied at a
later time. Unapplying is useful when you want to upgrade Magento with the diff
files provided by Varien.

To create a savepoint, run:

  $ fab set_host:user@host savepoint

This command will fail is there is no added, removed or modified files in the
repository.

TODO: this is unclear when we should commit changes as a changeset, or create an
MQ patch. MQ Patches are probably useful 

Upgrade Magento
~~~~~~~~~~~~~~~
When you want to upgrade Magento, just run the following command with the target
version:

  $ fab set_host:user@host upgrade:1.3.1

It will compare the current installed version, and will successively upgrade to
the wanted version, using each diff file. The location of the diff files is
known by the fabfile, so this procedure doesn't require any additional
information. If you have created savepoints, they will be unapplied so that the
upgrade of Magento won't fail due to unpatchable modifications.

TODO: the diff files may provide patches to some extensions not installed by
default (ex: blue or modern skin). In this case, the extension won't be
patched. This is a problem. The MQ patch should probably be used for alpha or
beta extensions, not for the stable or official ones?

Retrieve the deployment history
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Run:

  $ fab set_host:user@host get_glog

This is the same as running ``hg glog`` on the server.








