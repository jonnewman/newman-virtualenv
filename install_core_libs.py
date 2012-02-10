#--encode utf-8
import os
import re
import sys
import subprocess
import urllib

WINDOWS_PACKAGES = {
    'Crypto': 'pycrypto-2.3.win32-py2.6.msi',
    'mx':'egenix-mx-base-3.1.3.win32-py2.6.msi', 
    'wx':  'wxPython-2.8.11.0-py2.6-win32.exe',
    'win32api': 'pywin32-213.win32-py2.6.exe',
    'pyodbc': 'pyodbc-2.1.8.win32-py2.6.exe',
    'twisted': 'Twisted-10.1.0.winxp32-py2.6.exe',
    'PIL': 'PIL-1.1.6-py2.6.win32.zip',
    'lxml': 'lxml-2.3-py2.6-win32.egg',
    'netifaces': 'netifaces-0.5-py2.6-win32.egg'
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

if sys.platform == 'win32':
    NMROOT = cygpath(os.environ['NMROOT'])
    SITE_PACKAGES_DIR = cygpath(os.path.join(os.environ['VIRTUAL_ENV'], 'lib/site-packages'))
else:
    NMROOT = os.environ['NMROOT']
    SITE_PACKAGES_DIR = os.path.join(os.environ['VIRTUAL_ENV'], 'lib/site-packages')
BASKET = os.environ.get('BASKET', 'http://newmandistrib:Ewt9Gleb@distrib.newmanonline.org.uk/basket')
DOWNLOAD_DIR = os.path.join(NMROOT, 'var//download')
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

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

def pip_install(resource):
    child = subprocess.Popen(['pip', 'install', resource])
    child.communicate()
    return child.returncode

def easy_install(resource):
    child = subprocess.Popen(['easy_install', '-f' , BASKET, resource])
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

def install_packages(pkgs):
    failed_install = []
    for namespace in pkgs:
        print '=' * 40
        try:
            exec 'import %s' %namespace
            print '"%s" already installed' %namespace
        except (ImportError, SyntaxError):
            resource = pkgs[namespace]
            if resource.startswith('-e') or\
            resource.startswith('svn') or\
            resource.startswith('git') or\
            resource.startswith('hg'):
                returncode = pip_install(resource)
            else:
                returncode = easy_install(resource)
                if returncode != 0:
                    returncode = pip_install(resource)
            if returncode != 0:
                failed_install.append(resource)
    return failed_install
    
def install_windows_binaries(pkgs):
    failed_install = []
    missing_package = []
    for namespace in pkgs:
        print '=' * 40
        try:
            exec 'import %s' %namespace
            print '"%s" already installed' %namespace
        except (ImportError, SyntaxError):
            installer = pkgs[namespace]
            print 'install "%s" ' %installer
            succeed, full_path = get_installer(installer)
            if not succeed:
                missing_package.append(installer)
                failed_install.append(installer)
                continue
            if installer[-4:] == '.exe':
                #exe file try easy_install first of all
                returncode = easy_install(full_path)
                if returncode != 0:
                    print '*easy_install %s failed.' %installer
                    print 'now try to handle it as an installer created by Inno Setup'
                    returncode = install_innosetup_installer(full_path)
            elif installer[-4:] in ['.zip', '.egg', '.tgz'] or installer[-7:] == '.tar.gz':
                returncode = easy_install(full_path)
            elif installer[-4:] == '.msi':
                returncode = install_msi(full_path)
            else:
                returncode = 1
            if returncode == 0:
                print 'install file %s succeed!' %installer
            else:
                failed_install.append(installer)
    return failed_install, missing_package

def parse_arg():
    try:
        file_name = sys.argv[1]
        if os.path.exists(file_name):
            return file_name
        else:
            return None
    except IndexError:
        return None

def strip_version_info(pkg):
    pat = re.compile('(^.*?)(==|>=)(.*$)')
    mat = pat.match(pkg)
    if mat:
        pkg = mat.groups()[0]
    return pkg

def process_requirement_file(file_name):
    pkgs = {}
    if file_name:
        f = open(file_name, 'rb')
        for line in f:
            line = line.strip()
            #comment
            if line.startswith('#'):
                continue
            elif line.startswith('-e'):
                #-e ../newman-crypto
                #-e .
                if 'newman-' in line or line == '-e .':
                    continue
                else:
                    pkgs[line] = line
            elif 'newman-' in line:
                continue
            elif not line:
                continue
            else:
                try:
                    namespace, resource = line.split(',')
                except ValueError:
                    namespace = resource = line
                namespace = strip_version_info(namespace)
                pkgs[namespace] = resource
    return pkgs

def add_newman_pkgs_to_python_path():
    pass

def main():
    file_name = parse_arg()
    pkgs = process_requirement_file(file_name)
    add_newman_pkgs_to_python_path()
    failed_install = []
    missing_package = []
    if sys.platform == 'win32':
        failed, missing = install_windows_binaries(WINDOWS_PACKAGES)
        failed_install.extend(failed)
        missing_package.extend(missing)
    failed = install_packages(pkgs)
    failed_install.extend(failed)
    if failed_install:
        print '!failed to install package(s) %s' %failed_install
    if missing_package:
        print '!could not find package(s) %s from the basket %s' % (missing_package, BASKET)

if __name__ == '__main__':
    main()
