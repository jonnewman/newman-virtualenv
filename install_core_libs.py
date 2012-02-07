#--encode utf-8
import os
import sys
import subprocess
import urllib

PACKAGES = {
    'Crypto': 'pycrypto-2.3.win32-py2.6.msi',
    'mx':'egenix-mx-base-3.1.3.win32-py2.6.msi', 
    'wx':  'wxPython-2.8.11.0-py2.6-win32.exe',
    'win32api': 'pywin32-213.win32-py2.6.exe',
    'pyodbc': 'pyodbc-2.1.8.win32-py2.6.exe'
    }

def wget(url, download_dir='.'):
    def reporthook(a,b,c):
        sys.stdout.write('% 3.1f%% of %d bytes\r' %(min(100, float(a*b) /c * 100), c))
        sys.stdout.flush()
    i = url.rfind('/')
    file = os.path.join(download_dir, url[i+1:])
    print url, "->", file
    urllib.urlretrieve(url, file, reporthook)
    return file

def cygpath(path):
    path=subprocess.Popen(['cygpath', '-wa', path], stdout=subprocess.PIPE).communicate()[0].strip()
    return path

BASKET = os.environ['BASKET']
NMROOT = cygpath(os.environ['NMROOT'])
DOWNLOAD_DIR = os.path.join(NMROOT, 'var//download')
SITE_PACKAGES_DIR = cygpath(os.path.join(os.environ['VIRTUAL_ENV'], 'lib/site-packages'))

def get_installer(name):
    print 'get installer "%s"' %name
    full_path = os.path.abspath(os.path.join(DOWNLOAD_DIR, name))
    if os.path.exists(full_path):
        if '<title>404 Not Found</title>' not in open(full_path, 'r').read():
            print 'installer found on local directory "%s"' %DOWNLOAD_DIR
            return True, full_path
    url = BASKET + '/' + name
    wget(url, DOWNLOAD_DIR)
    if '<title>404 Not Found</title>' in open(full_path, 'r').read():
        return False, full_path
    else:
        return True, full_path

def easy_install(full_path):
    child = subprocess.Popen(['easy_install', full_path])
    child.communicate()
    return child.returncode

def install_innosetup_installer(full_path):
    child = subprocess.Popen([full_path, '/DIR=%s' %SITE_PACKAGES_DIR, '/VERYSILENT'])
    child.communicate()
    return child.returncode

def install_msi(full_path):
    child = subprocess.Popen(['msiexec.exe', '/a', full_path,
        'TARGETDIR=%s' %cygpath(os.environ['VIRTUAL_ENV']),
        '/quiet'])
    child.communicate()
    return child.returncode

def install_windows_packages():
    failed_install = []
    missing_package = []
    for namespace in PACKAGES:
        print '=' * 40
        try:
            exec 'import %s' %namespace
            print '"%s" already installed' %namespace
        except ImportError:
            installer = PACKAGES[namespace]
            print 'install "%s" ' %installer
            succeed, full_path = get_installer(installer)
            if not succeed:
                missing_package.append(installer)
                failed_install.append(installer)
                continue
            if installer.endswith('exe'):
                #exe file try easy_install first of all
                returncode = easy_install(full_path)
                if returncode != 0:
                    print '*easy_install %s failed.' %installer
                    print 'now try to handle it as an installer created by Inno Setup'
                    returncode = install_innosetup_installer(full_path)
                    if returncode == 0:
                        print 'install %s as an Inno Setup installer succeed!' %installer
                    else:
                        failed_install.append(installer)
            elif installer.endswith('msi'):
                returncode = install_msi(full_path)
                if returncode == 0:
                    print 'install msi file %s succeed!' %installer
                else:
                    failed_install.append(installer)
    if failed_install:
        print '!failed to install package(s) %s' %failed_install
    if missing_package:
        print '!could not find package(s) %s from %s' % (missing_package, BASKET)

def main():
    if sys.platform == 'win32':
        install_windows_packages()

if __name__ == '__main__':
    main()
