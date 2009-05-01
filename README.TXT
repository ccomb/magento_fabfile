=================================================
Easy Magento deployment with Fabric and Mercurial
=================================================

.. highlights::

  | Author : Christophe Combelles <ccomb@gorfou.fr>
  | for Emencia http://emencia.com


Magento
~~~~~~~
Magento is an eCommerce platform written in PHP. It allows you to create online
shops quickly and easily, with unprecedented flexibility and excellent usability.
Like almost any other PHP application, it can be installed very
easily, with two different methods:

 * download the full Magento archive, extract it on your hard disk, then upload all the files
   onto your server by FTP.

 * download a small downloader package, extract it on your hard disk, upload all
   the files onto your server by FTP, then access the downloader through your
   browser and let it finish downloading and installing the rest of Magento.

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

 * Immediately put the installation under version controli, to keep a full history
   of all the upgrades and customizations

 * Be able to remotely upgrade Magento with diff files provided by *Varien* (the company
   that distributes and maintains the Magento source code)

 * Be able to apply diffs, **even** if you heavily modified the Magento source code, or
   if you have a lot of installed extensions.

 * Instantly (and remotely) know which version is installed


To be able to achieve all these tasks, we will use three very good tools:

 * Fabric ( http://www.nongnu.org/fab/ )

 * Mercurial ( http://www.selenic.com/mercurial )

 * Mercurial MQ Extension ( http://www.selenic.com/mercurial/wiki/index.cgi/MqExtension )

Core idea
~~~~~~~~~

We will deploy Magento on the server in a Mercurial repository, so that
everything is versioned, and we will use Fabric to automate the deployment, the
upgrade, and the patches management.  The main Mercurial history will be used
for upgrades, and MQ patches will be used for extensions and customization.
During an upgrade, all patches are unapplied, diffs are applied, then patches
are reapplied. Mercurial is used to simulate a transactional system, so if an
upgrade fails, everything is safely reverted to the previous state.

Deployments and upgrades should be feasible without any Python, Fabric or
Mercurial knowledge.

Note that such a deployment leads to the exact same result as a manual
deployment. The only difference will be a ".hg" directory containing the
Mercurial repository. This directory is located one level higher than the
Magento installation, so it is not exposed to the web (provided your Apache
virtualhost points to the Magento directory).


Fabric
~~~~~~

Fabric is a simple tool that allows you to run remote commands on several
servers, upload files on these servers, and automate things by creating simple
commands.

For instance, we will be able to deploy Magento with a single command line like
this:

$ fab deploy:1.3.0

Installation
------------
Fabric is needed on your machine, not on the server.

To install Fabric, you first need to install Python, since Fabric is written in
Python. If you use a Debian or Ubuntu system, just run the following commands as
root (or prepend "sudo" if you're not root but sudoer):

# aptitude install python2.5 python-setuptools
# easy_install fabric

If you're using MacOs or Windows, the steps are similar: first check you have
Python 2.5, then easy_install fabric. Note that I have no idea whether Fabric
works on Windows or not.

You should now have a "fab" shell command. If you run this tool, you will
discover which commands are available. If your current shell directory contains a
"fabfile.py" file, additional commands are available.

Documentation
-------------

Currently here: http://www.nongnu.org/fab/documentation.html
Soon here: http://fabfile.org

Mercurial
~~~~~~~~~
Mercurial is a very fast, easy-to-use and well-known Distributed Version Control
System, used by large projects such as Mozilla, OpenJDK, OpenSolaris or Python.
If you already use Subversion, you will be able to use Mercurial in a matter of
minutes. The main conceptual difference is that every "checkout" is also a full
repository. So it is called a "clone" instead of a "checkout". Mercurial is much
more powerful than Subversion for branching and merging, and comes with a lot of
interesting plugins. It also avoids maintaining a central repository. When you
want to version a new project or directory, just run "hg init" and that's all.
Then you can start adding files in the repository and commit changes offline.
You will be able to synchronize your repository with another one, locally or
remotely.

Installation
------------
Mercurial is needed on the server, not on your machine.

Recent Linux systems already offer a Mercurial package. On Debian or Ubuntu, just
run the following command as root (or sudo) on your server:

# aptitude install mercurial

If you want a more recent version or if Mercurial is not already packaged, just
install it with easy_install:

# easy_install mercurial

Now you should enable the MQ Extension. This extension offers patch management,
just like "quilt" does, but integrated with Mercurial. It will be used for
Magento extensions and customisations.

Enable the MQ extension on the server by adding the following line in the
[hgext] section of your .hgrc.:

..
hgext.mq =



check environment
-----------------

deployment
----------
fab deploy



customization
-------------

upgrade
-------

