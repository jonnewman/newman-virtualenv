#--encode utf-8
import os
import sys
import subprocess
import urllib

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
    full_path = os.path.abspath(os.path.join(DOWNLOAD_DIR, name))
    if not os.path.exists(full_path):
        url = BASKET + '/' + name
        wget(url, DOWNLOAD_DIR)
    return full_path

def easy_install(installer):
    return subprocess.Popen(['easy_install', installer]).communicate()

def install_msi(installer):
    return subprocess.Popen(['msiexec.exe', '/a', installer,
        'TARGETDIR=%s' %cygpath(os.environ['VIRTUAL_ENV']),
        '/quiet']).communicate()

def install_wxpython():
    name = 'wxPython-2.8.11.0-py2.6-win32.exe'
    installer = get_installer(name)
    subprocess.Popen([installer, '/DIR=%s' %SITE_PACKAGES_DIR, '/VERYSILENT']).communicate()
    
def install_pywin32():
    name = 'pywin32-213.win32-py2.6.exe'
    installer = get_installer(name)
    easy_install(installer)

def install_egenix_mx_base():
    name = 'egenix-mx-base-3.1.3.win32-py2.6.msi'
    installer = get_installer(name)
    install_msi(installer)

def install_windows_specific():
    install_wxpython()
    install_pywin32()
    install_egenix_mx_base()
    
def main():
    if sys.platform == 'win32':
        install_windows_specific()

if __name__ == '__main__':
    main()
