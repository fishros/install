# -*- coding: utf-8 -*-
from calendar import c
import os
import re
import sys
import time
import subprocess
import importlib
import locale
from queue import Queue
import threading
import http.client
import time
from urllib.parse import urlparse


#TODO try import! failed skip
have_yaml_module = False
try:
    import yaml
    have_yaml_module = True
except:
    print('WARN:No Yaml Module!')

encoding = locale.getpreferredencoding()
encoding_utf8 = encoding.find("UTF")>-1


tr = None

class ConfigHelper():
    def __init__(self,record_file=None):
        self.record_input_queue = Queue()
        
        self.record_file = record_file
        if self.record_file==None: 
            # 首先检查环境变量
            self.record_file = os.environ.get('FISH_INSTALL_CONFIG', "./fish_install.yaml")
        self.default_input_queue = self.get_default_queue(self.record_file)

    def record_input(self,item):
        self.record_input_queue.put(item)
        
    def gen_config_file(self):
        """生产配置文件
        """
        config_yaml = {}

        chooses = []
            
        while self.record_input_queue.qsize()>0:
            chooses.append(self.record_input_queue.get())
            
        config_yaml['chooses'] = chooses
        config_yaml['time'] = str(time.time())
        
        # 先写入临时文件，再使用sudo移动到目标位置
        temp_path = "/tmp/fish_install_temp.yaml"
        target_path = "/tmp/fish_install.yaml"
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                if have_yaml_module:
                    yaml.dump(config_yaml, f, allow_unicode=True)
            
            # 检查目标文件是否存在
            if os.path.exists(target_path):
                # 在自动化测试环境中，直接覆盖原配置文件
                if os.environ.get('GITHUB_ACTIONS') == 'true':
                    print("检测到GitHub Actions环境，直接覆盖已存在的配置文件: {}".format(target_path))
                else:
                    print("检测到已存在的配置文件: {}".format(target_path))
                    user_input = input("是否替换该文件？[y/N]: ")
                    if user_input.lower() not in ['y', 'yes']:
                        print("取消替换，保留原配置文件")
                        os.remove(temp_path)  # 删除临时文件
                        return
            
            # 先尝试删除目标文件（如果存在），避免mv命令的交互提示
            if os.path.exists(target_path):
                try:
                    os.remove(target_path)
                except PermissionError:
                    # 如果普通权限无法删除，则使用sudo
                    print("使用sudo权限删除已存在的配置文件...")
                    os.system("sudo rm -f {}".format(target_path))
            
            # 使用mv命令移动文件，避免权限问题
            result = os.system("mv {} {}".format(temp_path, target_path))
            if result == 0:
                print("配置文件已保存至: {}".format(target_path))
            else:
                # 如果普通权限移动失败，则尝试使用sudo
                print("尝试使用sudo权限保存配置文件...")
                result = os.system("sudo mv {} {}".format(temp_path, target_path))
                if result == 0:
                    print("配置文件已保存至: {} (使用sudo权限)".format(target_path))
                else:
                    print("配置文件保存失败")
        except Exception as e:
            print("配置文件生成过程中发生错误: {}".format(str(e)))
            # 清理临时文件（如果存在）
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def get_input_value(self):
        if self.default_input_queue.qsize()>0:
            return self.default_input_queue.get()
        
    def record_choose(self,data):
        self.record_input_queue.put(data)
    
    def get_default_queue(self,param_file_path):
        """获取默认的配置

        Args:
            param_file_path (string, optional): 参数文件路径. Defaults to None.

        Returns:
            Queue: 数据队列
        """
        config_data = None
        choose_queue = Queue()

        if not have_yaml_module:return choose_queue
        
        if not os.path.exists(param_file_path): 
            return choose_queue
        
        with open(param_file_path,"r",encoding="utf-8") as f:
            config_data = f.read()
        
        if config_data == None: return choose_queue

        if hasattr(yaml,'FullLoader'):
            config_yaml = yaml.load(config_data,Loader=yaml.FullLoader)
        else:
            config_yaml = yaml.load(config_data)
            
        for choose in config_yaml['chooses']:
            choose_queue.put(choose)
        
        return choose_queue

config_helper = ConfigHelper()

def GetOsVersion():
    """
    Library for detecting the current OS, including detecting specific
    Linux distributions.
    """
    import codecs
    # to be removed after Ubuntu Xenial is out of support
    import sys
    # @TODO 系统的python版本小于3.8，Conda版本>3.8
    if sys.version_info >= (3, 8):
        import distro
    else:
        import platform as distro
    import locale
    import os
    import platform
    import subprocess


    def _read_stdout(cmd):
        try:
            pop = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (std_out, std_err) = pop.communicate()
            # Python 2.6 compatibility
            if isinstance(std_out, str):
                return std_out.strip()
            return std_out.decode(encoding='UTF-8').strip()
        except:
            return None


    def uname_get_machine():
        """
        Linux: wrapper around uname to determine if OS is 64-bit
        """
        return _read_stdout(['uname', '-m'])


    def read_issue(filename="/etc/issue"):
        """
        :returns: list of strings in issue file, or None if issue file cannot be read/split
        """
        if os.path.exists(filename):
            with codecs.open(filename, 'r', encoding=locale.getpreferredencoding()) as f:
                return f.read().split()
        return None


    def read_os_release(filename=None):
        """
        :returns: Dictionary of key value pairs from /etc/os-release or fallback to 
        /usr/lib/os-release, with quotes stripped from values
        """
        if filename is None:
            filename = '/etc/os-release'
            if not os.path.exists(filename):
                filename = '/usr/lib/os-release'

        if not os.path.exists(filename):
            return None

        release_info = {}
        with codecs.open(filename, 'r', encoding=locale.getpreferredencoding()) as f:
            for line in f:
                key, val = line.rstrip('\n').partition('=')[::2]
                release_info[key] = val.strip('"')
        return release_info


    class OsNotDetected(Exception):
        """
        Exception to indicate failure to detect operating system.
        """
        pass


    class OsDetector(object):
        """
        Generic API for detecting a specific OS.
        """
        def is_os(self):
            """
            :returns: if the specific OS which this class is designed to
            detect is present.  Only one version of this class should
            return for any version.
            """
            raise NotImplementedError("is_os unimplemented")

        def get_version(self):
            """
            :returns: standardized version for this OS. (aka Ubuntu Hardy Heron = "8.04")
            :raises: :exc:`OsNotDetected` if called on incorrect OS.
            """
            raise NotImplementedError("get_version unimplemented")

        def get_codename(self):
            """
            :returns: codename for this OS. (aka Ubuntu Hardy Heron = "hardy").  If codenames are not available for this OS, return empty string.
            :raises: :exc:`OsNotDetected` if called on incorrect OS.
            """
            raise NotImplementedError("get_codename unimplemented")


    class LsbDetect(OsDetector):
        """
        Generic detector for Debian, Ubuntu, Mint, and Pop! OS
        """
        def __init__(self, lsb_name, get_version_fn=None):
            self.lsb_name = lsb_name
            if hasattr(distro, "linux_distribution"):
                self.lsb_info = distro.linux_distribution(full_distribution_name=0)
            elif hasattr(distro, "dist"):
                self.lsb_info = distro.dist()
            else:
                self.lsb_info = None

        def is_os(self):
            if self.lsb_info is None:
                return False
            # Work around platform returning 'Ubuntu' and distro returning 'ubuntu'
            return self.lsb_info[0].lower() == self.lsb_name.lower()

        def get_version(self):
            if self.is_os():
                return self.lsb_info[1]
            raise OsNotDetected('called in incorrect OS')

        def get_codename(self):
            if self.is_os():
                # fix Jammy Error
                return self.lsb_info[2].split(" ")[0].lower()
            raise OsNotDetected('called in incorrect OS')


    class Debian(LsbDetect):

        def __init__(self, get_version_fn=None):
            super(Debian, self).__init__('debian', get_version_fn)

        def get_codename(self):
            if self.is_os():
                v = self.get_version()
                if v.startswith('7.'):
                    return 'wheezy'
                if v.startswith('8.'):
                    return 'jessie'
                if v.startswith('9.'):
                    return 'stretch'
                if v.startswith('10.'):
                    return 'buster'
                return ''


    class FdoDetect(OsDetector):
        """
        Generic detector for operating systems implementing /etc/os-release, as defined by the os-release spec hosted at Freedesktop.org (Fdo):
        http://www.freedesktop.org/software/systemd/man/os-release.html
        Requires that the "ID", and "VERSION_ID" keys are set in the os-release file.

        Codename is parsed from the VERSION key if available: either using the format "foo, CODENAME" or "foo (CODENAME)."
        If the VERSION key is not present, the VERSION_ID is value is used as the codename.
        """
        def __init__(self, fdo_id):
            release_info = read_os_release()
            if release_info is not None and "ID" in release_info and release_info["ID"] == fdo_id:
                self.release_info = release_info
            else:
                self.release_info = None

        def is_os(self):
            return self.release_info is not None and "VERSION_ID" in self.release_info

        def get_version(self):
            if self.is_os():
                return self.release_info["VERSION_ID"]
            raise OsNotDetected("called in incorrect OS")

        def get_codename(self):
            if self.is_os():
                if "VERSION" in self.release_info:
                    version = self.release_info["VERSION"]
                    # FDO style: works with Fedora, Debian, Suse.
                    if '(' in version:
                        codename = version[version.find("(") + 1:version.find(")")]
                    # Ubuntu style
                    elif '"' in version:
                        codename = version[version.find(",") + 1:].lstrip(' ').split()[0]
                    # Indeterminate style
                    else:
                        codename = version
                    return codename.lower()
                else:
                    return self.get_version()
            raise OsNotDetected("called in incorrect OS")


    class OpenEmbedded(OsDetector):
        """
        Detect OpenEmbedded.
        """
        def is_os(self):
            return "ROS_OS_OVERRIDE" in os.environ and os.environ["ROS_OS_OVERRIDE"] == "openembedded"

        def get_version(self):
            if self.is_os():
                return ""
            raise OsNotDetected('called in incorrect OS')

        def get_codename(self):
            if self.is_os():
                return ""
            raise OsNotDetected('called in incorrect OS')


    class OpenSuse(OsDetector):
        """
        Detect OpenSuse OS.
        """
        def __init__(self, brand_file="/etc/SuSE-brand", release_file="/etc/SuSE-release"):
            self._brand_file = brand_file
            self._release_file = release_file

        def is_os(self):
            os_list = read_issue(self._brand_file)
            return os_list and os_list[0] == "openSUSE"

        def get_version(self):
            if self.is_os() and os.path.exists(self._brand_file):
                with open(self._brand_file, 'r') as fh:
                    os_list = fh.read().strip().split('\n')
                    if len(os_list) == 2:
                        os_list = os_list[1].split(' = ')
                        if os_list[0] == "VERSION":
                            return os_list[1]
            raise OsNotDetected('cannot get version on this OS')

        def get_codename(self):
            # /etc/SuSE-release is deprecated since 13.1
            if self._release_file is None:
                return ""
            if self.is_os() and os.path.exists(self._release_file):
                with open(self._release_file, 'r') as fh:
                    os_list = fh.read().strip().split('\n')
                    for line in os_list:
                        kv = line.split(' = ')
                        if kv[0] == "CODENAME":
                            return kv[1]
            raise OsNotDetected('called in incorrect OS')


    # Source: https://en.wikipedia.org/wiki/MacOS#Versions
    _osx_codename_map = {
    '10.4': 'tiger',
    '10.5': 'leopard',
    '10.6': 'snow',
    '10.7': 'lion',
    '10.8': 'mountain lion',
    '10.9': 'mavericks',
    '10.10': 'yosemite',
    '10.11': 'el capitan',
    '10.12': 'sierra',
    '10.13': 'high sierra',
    '10.14': 'mojave',
    '10.15': 'catalina',
    '11': 'big sur'
    }


    def _osx_codename(major, minor):
        if major == 10:
            key = '%s.%s' % (major, minor)
        else:
            key = '%s' % (major)        
        if key not in _osx_codename_map:
            raise OsNotDetected("unrecognized version: %s" % key)
        return _osx_codename_map[key]


    class OSX(OsDetector):
        """
        Detect OS X
        """
        def __init__(self, sw_vers_file="/usr/bin/sw_vers"):
            self._sw_vers_file = sw_vers_file

        def is_os(self):
            return os.path.exists(self._sw_vers_file)

        def get_codename(self):
            if self.is_os():
                version = self.get_version()
                import distutils.version  # To parse version numbers
                try:
                    ver = distutils.version.StrictVersion(version).version
                except ValueError:
                    raise OsNotDetected("invalid version string: %s" % (version))
                return _osx_codename(*ver[0:2])
            raise OsNotDetected('called in incorrect OS')

        def get_version(self):
            if self.is_os():
                return _read_stdout([self._sw_vers_file, '-productVersion'])
            raise OsNotDetected('called in incorrect OS')


    class QNX(OsDetector):
        '''
        Detect QNX realtime OS.
        @author: Isaac Saito
        '''
        def __init__(self, uname_file='/bin/uname'):
            '''
            @param uname_file: An executable that can be used for detecting
                            OS name and version.
            '''
            self._os_name_qnx = 'QNX'
            self._uname_file = uname_file

        def is_os(self):
            if os.path.exists(self._uname_file):
                std_out = _read_stdout([self._uname_file])
                return std_out.strip() == self._os_name_qnx
            else:
                return False

        def get_codename(self):
            if self.is_os():
                return ''
            raise OsNotDetected('called in incorrect OS')

        def get_version(self):
            if self.is_os() and os.path.exists(self._uname_file):
                return _read_stdout([self._uname_file, "-r"])
            raise OsNotDetected('called in incorrect OS')


    class Arch(OsDetector):
        """
        Detect Arch Linux.
        """
        def __init__(self, release_file='/etc/arch-release'):
            self._release_file = release_file

        def is_os(self):
            return os.path.exists(self._release_file)

        def get_version(self):
            if self.is_os():
                return ""
            raise OsNotDetected('called in incorrect OS')

        def get_codename(self):
            if self.is_os():
                return ""
            raise OsNotDetected('called in incorrect OS')


    class Manjaro(Arch):
        """
        Detect Manjaro.
        """
        def __init__(self, release_file='/etc/manjaro-release'):
            super(Manjaro, self).__init__(release_file)


    class Cygwin(OsDetector):
        """
        Detect Cygwin presence on Windows OS.
        """
        def is_os(self):
            return os.path.exists("/usr/bin/cygwin1.dll")

        def get_version(self):
            if self.is_os():
                return _read_stdout(['uname', '-r'])
            raise OsNotDetected('called in incorrect OS')

        def get_codename(self):
            if self.is_os():
                return ''
            raise OsNotDetected('called in incorrect OS')


    class Gentoo(OsDetector):
        """
        Detect Gentoo OS.
        """
        def __init__(self, release_file="/etc/gentoo-release"):
            self._release_file = release_file

        def is_os(self):
            os_list = read_issue(self._release_file)
            return os_list and os_list[0] == "Gentoo" and os_list[1] == "Base"

        def get_version(self):
            if self.is_os():
                os_list = read_issue(self._release_file)
                return os_list[4]
            raise OsNotDetected('called in incorrect OS')

        def get_codename(self):
            if self.is_os():
                return ''
            raise OsNotDetected('called in incorrect OS')


    class Funtoo(Gentoo):
        """
        Detect Funtoo OS, a Gentoo Variant.
        """
        def __init__(self, release_file="/etc/gentoo-release"):
            Gentoo.__init__(self, release_file)

        def is_os(self):
            os_list = read_issue(self._release_file)
            return os_list and os_list[0] == "Funtoo" and os_list[1] == "Linux"


    class FreeBSD(OsDetector):
        """
        Detect FreeBSD OS.
        """
        def __init__(self, uname_file="/usr/bin/uname"):
            self._uname_file = uname_file

        def is_os(self):
            if os.path.exists(self._uname_file):
                std_out = _read_stdout([self._uname_file])
                return std_out.strip() == "FreeBSD"
            else:
                return False

        def get_version(self):
            if self.is_os() and os.path.exists(self._uname_file):
                return _read_stdout([self._uname_file, "-r"])
            raise OsNotDetected('called in incorrect OS')

        def get_codename(self):
            if self.is_os():
                return ''
            raise OsNotDetected('called in incorrect OS')


    class Slackware(OsDetector):
        """
        Detect SlackWare Linux.
        """
        def __init__(self, release_file='/etc/slackware-version'):
            self._release_file = release_file

        def is_os(self):
            return os.path.exists(self._release_file)

        def get_version(self):
            if self.is_os():
                os_list = read_issue(self._release_file)
                return os_list[1]
            raise OsNotDetected('called in incorrect OS')

        def get_codename(self):
            if self.is_os():
                return ''
            raise OsNotDetected('called in incorrect OS')


    class Windows(OsDetector):
        """
        Detect Windows OS.
        """
        def is_os(self):
            return platform.system() == "Windows"

        def get_version(self):
            if self.is_os():
                return platform.version()
            raise OsNotDetected('called in incorrect OS')

        def get_codename(self):
            if self.is_os():
                return platform.release()
            raise OsNotDetected('called in incorrect OS')


    class OsDetect:
        """
        This class will iterate over registered classes to lookup the
        active OS and version
        """

        default_os_list = []

        def __init__(self, os_list=None):
            if os_list is None:
                os_list = OsDetect.default_os_list
            self._os_list = os_list
            self._os_name = None
            self._os_version = None
            self._os_codename = None
            self._os_detector = None
            self._override = False

        @staticmethod
        def register_default(os_name, os_detector):
            """
            Register detector to be used with all future instances of
            :class:`OsDetect`.  The new detector will have precedence over
            any previously registered detectors associated with *os_name*.

            :param os_name: OS key associated with OS detector
            :param os_detector: :class:`OsDetector` instance
            """
            OsDetect.default_os_list.insert(0, (os_name, os_detector))

        def detect_os(self, env=None):
            """
            Detect operating system.  Return value can be overridden by
            the :env:`ROS_OS_OVERRIDE` environment variable.

            :param env: override ``os.environ``
            :returns: (os_name, os_version, os_codename), ``(str, str, str)``
            :raises: :exc:`OsNotDetected` if OS could not be detected
            """
            if env is None:
                env = os.environ
            if 'ROS_OS_OVERRIDE' in env:
                splits = env["ROS_OS_OVERRIDE"].split(':')
                self._os_name = splits[0]
                if len(splits) > 1:
                    self._os_version = splits[1]
                    if len(splits) > 2:
                        self._os_codename = splits[2]
                    else:
                        self._os_codename = ''
                else:
                    self._os_version = self._os_codename = ''
                self._override = True
            else:
                for os_name, os_detector in self._os_list:
                    if os_detector.is_os():
                        self._os_name = os_name
                        self._os_version = os_detector.get_version()
                        self._os_codename = os_detector.get_codename()
                        self._os_detector = os_detector
                        break

            if self._os_name:
                return self._os_name, self._os_version, self._os_codename
            else:  # No solution found
                attempted = [x[0] for x in self._os_list]
                raise OsNotDetected("Could not detect OS, tried %s" % attempted)

        def get_detector(self, name=None):
            """
            Get detector used for specified OS name, or the detector for this OS if name is ``None``.

            :raises: :exc:`KeyError`
            """
            if name is None:
                if not self._os_detector:
                    self.detect_os()
                return self._os_detector
            else:
                try:
                    return [d for d_name, d in self._os_list if d_name == name][0]
                except IndexError:
                    raise KeyError(name)

        def add_detector(self, name, detector):
            """
            Add detector to list of detectors used by this instance.  *detector* will override any previous
            detectors associated with *name*.

            :param name: OS name that detector matches
            :param detector: :class:`OsDetector` instance
            """
            self._os_list.insert(0, (name, detector))

        def get_name(self):
            if not self._os_name:
                self.detect_os()
            return self._os_name

        def get_version(self):
            if not self._os_version:
                self.detect_os()
            return self._os_version

        def get_codename(self):
            if not self._os_codename:
                self.detect_os() 
                self._os_codename = self._os_codename.lower()
                if len(self._os_codename.split(" "))>1:
                    self._os_codename=self._os_codename.split(" ")[0]
            return self._os_codename


    OS_ALMALINUX = 'almalinux'
    OS_ALPINE = 'alpine'
    OS_AMAZON = 'amazon'
    OS_ARCH = 'arch'
    OS_BUILDROOT = 'buildroot'
    OS_MANJARO = 'manjaro'
    OS_CENTOS = 'centos'
    OS_EULEROS = 'euleros'
    OS_CYGWIN = 'cygwin'
    OS_DEBIAN = 'debian'
    OS_BULLEYE = 'bullseye'
    OS_ELEMENTARY = 'elementary'
    OS_ELEMENTARY_OLD = 'elementary'
    OS_FEDORA = 'fedora'
    OS_FREEBSD = 'freebsd'
    OS_FUNTOO = 'funtoo'
    OS_GENTOO = 'gentoo'
    OS_LINARO = 'linaro'
    OS_MINT = 'mint'
    OS_MX = 'mx'
    OS_NEON = 'neon'
    OS_OPENEMBEDDED = 'openembedded'
    OS_OPENSUSE = 'opensuse'
    OS_OPENSUSE13 = 'opensuse'
    OS_ORACLE = 'oracle'
    OS_TIZEN = 'tizen'
    OS_SAILFISHOS = 'sailfishos'
    OS_OSX = 'osx'
    OS_POP = 'pop'
    OS_QNX = 'qnx'
    OS_RHEL = 'rhel'
    OS_ROCKY = 'rocky'
    OS_SLACKWARE = 'slackware'
    OS_UBUNTU = 'ubuntu'
    OS_CLEARLINUX = 'clearlinux'
    OS_NIXOS = 'nixos'
    OS_WINDOWS = 'windows'
    OS_ZORIN =  'zorin'

    OsDetect.register_default(OS_ALMALINUX, FdoDetect("almalinux"))
    OsDetect.register_default(OS_ALPINE, FdoDetect("alpine"))
    OsDetect.register_default(OS_AMAZON, FdoDetect("amzn"))
    OsDetect.register_default(OS_ARCH, Arch())
    OsDetect.register_default(OS_BUILDROOT, FdoDetect("buildroot"))
    OsDetect.register_default(OS_MANJARO, Manjaro())
    OsDetect.register_default(OS_CENTOS, FdoDetect("centos"))
    OsDetect.register_default(OS_EULEROS, FdoDetect("euleros"))
    OsDetect.register_default(OS_CYGWIN, Cygwin())
    OsDetect.register_default(OS_DEBIAN, Debian())
    OsDetect.register_default(OS_ELEMENTARY, LsbDetect("elementary"))
    OsDetect.register_default(OS_ELEMENTARY_OLD, LsbDetect("elementary OS"))
    OsDetect.register_default(OS_FEDORA, FdoDetect("fedora"))
    OsDetect.register_default(OS_FREEBSD, FreeBSD())
    OsDetect.register_default(OS_FUNTOO, Funtoo())
    OsDetect.register_default(OS_GENTOO, Gentoo())
    OsDetect.register_default(OS_LINARO, LsbDetect("Linaro"))
    OsDetect.register_default(OS_MINT, LsbDetect("LinuxMint"))
    OsDetect.register_default(OS_MX, LsbDetect("MX"))
    OsDetect.register_default(OS_NEON, LsbDetect("neon"))
    OsDetect.register_default(OS_OPENEMBEDDED, OpenEmbedded())
    OsDetect.register_default(OS_OPENSUSE, OpenSuse())
    OsDetect.register_default(OS_OPENSUSE13, OpenSuse(brand_file='/etc/SUSE-brand', release_file=None))
    OsDetect.register_default(OS_OPENSUSE, FdoDetect("opensuse-tumbleweed"))
    OsDetect.register_default(OS_OPENSUSE, FdoDetect("opensuse-leap"))
    OsDetect.register_default(OS_OPENSUSE, FdoDetect("opensuse"))
    OsDetect.register_default(OS_ORACLE, FdoDetect("ol"))
    OsDetect.register_default(OS_TIZEN, FdoDetect("tizen"))
    OsDetect.register_default(OS_SAILFISHOS, FdoDetect("sailfishos"))
    OsDetect.register_default(OS_OSX, OSX())
    OsDetect.register_default(OS_POP, LsbDetect("Pop"))
    OsDetect.register_default(OS_QNX, QNX())
    OsDetect.register_default(OS_RHEL, FdoDetect("rhel"))
    OsDetect.register_default(OS_ROCKY, FdoDetect("rocky"))
    OsDetect.register_default(OS_SLACKWARE, Slackware())
    OsDetect.register_default(OS_UBUNTU, LsbDetect("Ubuntu"))
    OsDetect.register_default(OS_CLEARLINUX, FdoDetect("clear-linux-os"))
    OsDetect.register_default(OS_NIXOS, FdoDetect("nixos"))
    OsDetect.register_default(OS_WINDOWS, Windows())
    OsDetect.register_default(OS_ZORIN, LsbDetect("Zorin"))


    detect = OsDetect()
    return detect

osversion = GetOsVersion()

class Tracking():
    """
    日志跟踪模块
    """
    logs = []
    err_logs = []
    need_report = False
    def put_log(values,end=""):
        Tracking.logs.append((values,end))
    
    def put_cmd_result(code,out,err,command):
        if code!=0:
            Tracking.need_report = True
            Tracking.err_logs.append("Execute Command: {} Error Code{}".format(command,code))
            Tracking.err_logs.append('====================OUT====================')
            for line in out:
                Tracking.err_logs.append(line)
            Tracking.err_logs.append('====================ERR====================')
            for line in err:
                Tracking.err_logs.append(line)


class PrintUtils():
    
    @staticmethod
    def print_delay(data,delay=0.03,end="\n"):
        PrintUtils.print_text("\033[37m",end="")
        for d in data:
            d = d.encode("utf-8").decode("utf-8")
            PrintUtils.print_text("{}".format(d),end="",flush=True)
            time.sleep(delay)
        PrintUtils.print_text(end=end)

    @staticmethod
    def print_error(data,end="\n"):
        PrintUtils.print_text("\033[31m{}\033[37m".format(data),end=end)

    @staticmethod
    def print_info(data,end="\n"):
        PrintUtils.print_text("\033[37m{}".format(data),end=end)

    @staticmethod
    def print_success(data,end="\n"):
        PrintUtils.print_text("\033[32m{}\033[37m".format(data),end=end)

    @staticmethod
    def print_warn(data,end="\n"):
        PrintUtils.print_text("\033[33m{}\033[37m".format(data),end=end)

    @staticmethod
    def print_text(values="",end="\n",flush= False):
        print(values,end=str(end),flush=flush) # force to string
        Tracking.put_log(values,end=end)
        
    @staticmethod
    def print_fish(timeout=1,scale=30):
        return 
        start = time.perf_counter()
        for i in range(scale + 1):
            a = "🐟" * i
            b = ".." * (scale - i)
            c = (i / scale) * 100
            dur = time.perf_counter() - start
            print("\r{:^3.0f}%[{}->{}]{:.2f}s".format(c,a,b,dur),end = "")
            time.sleep(timeout/scale)
        print("\n")




class Task():
    """
    - type: 任务类型
    - params: 任务参数
    - result: 任务执行结果
    - progress: 任务执行进度
    - timeout: 任务超时时间 
    - subtask: 子任务
    """
    TASK_TYPE_CMD = 0
    TASK_TYPE_CHOOSE = 1
    TASK_TYPE_PATTERN= 2
    def __init__(self,type) -> None:
        self.type = Task.TASK_TYPE_CMD 
    def run(self):
        pass


class Progress():
    import shutil

    # 获取终端的行宽
    terminal_size = shutil.get_terminal_size()
    line_width = terminal_size.columns

    def __init__(self,timeout=10,scale=20) -> None:
        self.timeout = timeout
        self.start = time.perf_counter()
        self.dur  = time.perf_counter() -self.start 
        self.scale = scale
        self.i = 0
        self.latest_log = ""

    def update(self,log=""):
        if (self.i%4) == 0: 
            PrintUtils.print_text('\r[/][{:.2f}s] {}'.format(self.dur,log),end="")
        elif(self.i%4) == 1: 
            PrintUtils.print_text('\r[\\][{:.2f}s] {}'.format(self.dur,log),end="")
        elif (self.i%4) == 2: 
            PrintUtils.print_text('\r[|][{:.2f}s] {}'.format(self.dur,log),end="")
        elif (self.i%4) == 3: 
            PrintUtils.print_text('\r[-][{:.2f}s] {}'.format(self.dur,log),end="")
        sys.stdout.flush()
        self.i += 1
        # update time
        self.latest_log = log
        self.dur  = time.perf_counter() -self.start 

    def update_time(self):
        log = self.latest_log
        if (self.i%4) == 0: 
            print('\r[/][{:.2f}s] {}'.format(self.dur,log),end="")
        elif(self.i%4) == 1: 
            print('\r[\\][{:.2f}s] {}'.format(self.dur,log),end="")
        elif (self.i%4) == 2: 
            print('\r[|][{:.2f}s] {}'.format(self.dur,log),end="")
        elif (self.i%4) == 3: 
            print('\r[-][{:.2f}s] {}'.format(self.dur,log),end="")
        sys.stdout.flush()
        self.dur  = time.perf_counter() -self.start 


    def finsh(self,log="",color='\033[32m'):
        log = log+" "*(Progress.line_width-len(log)-15) 
        PrintUtils.print_text('\r{}[-][{:.2f}s] {}'.format(color,self.dur, log), end="\r\n\r\n")



class CmdTask(Task):
    def __init__(self,command,timeout=0,groups=False,os_command=False,path=None,executable='/bin/sh') -> None:
        super().__init__(Task.TASK_TYPE_CMD)
        self.command = command
        self.timeout = timeout
        self.os_command = os_command
        self.cwd = path
        self.executable = executable

    def getlog(self,callback=None):
        stdout_line = ""
        for line in iter(self.sub.stdout.readline,'b'):
            line = line.rstrip()#.decode('utf8', errors="ignore")
            if callback and line:
                callback(line,'out')
            if(subprocess.Popen.poll(self.sub) is not None):
                if(line==""):
                    break

        for line in iter(self.sub.stderr.readline,'b'):
            line = line.rstrip()#.decode('utf8', errors="ignore")
            if callback and line:
                callback(line,'err')
            if(subprocess.Popen.poll(self.sub) is not None):
                if(line==""):
                    break

    def getlogs(self):
        out = []
        lines = self.sub.stdout.readlines()
        for line in lines:
            line = line.decode("utf-8", errors="ignore").strip()
            if line:
                out.append(line)
            time.sleep(0.001)
        lines = self.sub.stderr.readlines()
        for line in lines:
            line = line.decode("utf-8", errors="ignore").strip()
            if line:
                out.append(line)
            time.sleep(0.001)

        logstr = ""
        for log in out:
            logstr += log
        return logstr


    def command_thread(self,executable='/bin/sh'):
        self.ret_ok = False
        out,err = [],[]
        self.sub = subprocess.Popen(self.command,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    cwd=self.cwd,
                                    shell=True,
                                    bufsize=1,  # Line buffered
                                    universal_newlines=True)
        self.bar = Progress()
        err = []
        out = []
        def log_callback(log,log_type):
            self.bar.update(log)
            if log_type=='out':
                out.append(log)
            else:
                err.append(log)

        self.getlog(log_callback)
        code = self.sub.returncode

        msg = 'code:{}'.format(code)
        if code == 0: msg="success"
        self.ret_code = code

        if code==0:
            self.bar.finsh('CMD Result:{}'.format(msg),'\033[37m')
        else:
            self.bar.finsh('CMD Result:{}'.format(msg),'\033[31m')


        self.ret_out = out
        self.ret_err = err
        self.ret_ok = True

    def run_command(self,executable='/bin/sh'):
        self.command_thread = threading.Thread(target=self.command_thread)
        self.command_thread.start()
        time.sleep(0.5) # 等待线程启动
        while self.is_command_finish()==-1:
            self.bar.update_time()
            time.sleep(0.1)

        start_time = time.time()
        while not self.ret_ok and time.time()-start_time < 2.0: # 2s timeout wait  command_thread end
            time.sleep(0.1)

        Tracking.put_cmd_result(self.ret_code,self.ret_out,self.ret_err,self.command)
        return (self.ret_code,self.ret_out,self.ret_err)

    def is_command_finish(self):
        # poll 是返回码
        if self.sub.poll() == None:
            return -1
        return self.sub.poll()

    def run_os_command(self):
        """
        退出即结束
        """
        if self.cwd is not None:
            os.system("cd {} && {}".format(self.cwd,self.command))
        else:
            os.system(self.command)

    def run(self):
        PrintUtils.print_info("\033[32mRun CMD Task:[{}]".format(self.command))
        if self.os_command:
            return self.run_os_command()
        return self.run_command()


class ChooseTask(Task):
    def __init__(self,dic,tips,array=False) -> None:
        self.tips= tips
        self.dic = dic
        self.array = array
        super().__init__(Task.TASK_TYPE_CHOOSE)

    @staticmethod
    def __choose(data,tips,array):
        if array:
            count = 1
            dic = {}
            for e in data:
                dic[count] = e
                count += 1
        else:
            dic = data
        dic[0]="quit"
        # 0 quit
        choose = -1 
        for key in dic:
            PrintUtils.print_delay('[{}]:{}'.format(key,tr.tr(dic[key])),0.005)
            
        choose = None
        choose_item = config_helper.get_input_value()

        while True:
            if choose_item:
                choose = str(choose_item['choose'])
                PrintUtils.print_text(tr.tr("为您从配置文件找到默认选项：")+str(choose_item))
            else:
                try:
                    choose = input(tr.tr("请输入[]内的数字以选择:"))
                    choose_item = None
                except EOFError:
                    # 在自动化测试环境中，input()可能会引发EOFError
                    # 如果是从配置文件读取的选项，则使用它，否则返回默认值0（退出）
                    if choose_item:
                        choose = str(choose_item['choose'])
                    else:
                        choose = "0"  # 默认选择退出
                    PrintUtils.print_text(tr.tr("检测到自动化环境，使用默认选项: {}").format(choose))
            # Input From Queue
            if choose.isdecimal() :
                if (int(choose) in dic.keys() ) or (int(choose)==0):
                    choose = int(choose)
                    break
        config_helper.record_choose({"choose":choose,"desc":dic[choose]})
        PrintUtils.print_fish()
        return choose,dic[choose]

    def run(self):
        PrintUtils.print_delay(tr.tr("RUN Choose Task:[请输入括号内的数字]"))
        PrintUtils.print_delay(self.tips,0.001)
        return ChooseTask.__choose(self.dic,self.tips,self.array)


class ChooseWithCategoriesTask(Task):
    def __init__(self,dic,tips,categories,array=False) -> None:
        self.tips= tips
        self.dic = dic
        self.array = array
        self.categories = categories
        super().__init__(Task.TASK_TYPE_CHOOSE)

    @staticmethod
    def __choose(data,tips,array,categories):
        dic = data
        # dic[0]="quit"
        # 0 quit
        choose_id = -1 

        tool_ids = [0]
        # 打印不同类型工具的分类结果
        for tool_type, tools_list in dic.items():
            PrintUtils.print_delay("{}:".format(tr.tr(categories[tool_type])),0.005)
            sortkeys = sorted(tools_list.keys())
            for tool_id in sortkeys:
                PrintUtils.print_delay("  [{}]:{}".format(tool_id,tr.tr(tools_list[tool_id]['tip'])),0.005)
                tool_ids.append(tool_id)
            print()
        PrintUtils.print_delay("[0]:quit\n",0.005)

        choose = None
        choose_item = config_helper.get_input_value()

        while True:
            if choose_item:
                choose_id = str(choose_item['choose'])
                print(tr.tr("为您从配置文件找到默认选项：")+str(choose_item))
            else:
                try:
                    choose_id = input(tr.tr("请输入[]内的数字以选择:"))
                    choose_item = None
                except EOFError:
                    # 在自动化测试环境中，input()可能会引发EOFError
                    # 如果是从配置文件读取的选项，则使用它，否则返回默认值0（退出）
                    if choose_item:
                        choose_id = str(choose_item['choose'])
                    else:
                        choose_id = "0"  # 默认选择退出
                    PrintUtils.print_text(tr.tr("检测到自动化环境，使用默认选项: {}").format(choose_id))
            # Input From Queue
            if choose_id.isdecimal() :
                if int(choose_id) in tool_ids :
                    choose_id = int(choose_id)
                    break
        config_helper.record_choose({"choose":choose_id,"desc":""})
        PrintUtils.print_fish()
        return choose_id,""

    def run(self):
        PrintUtils.print_delay(tr.tr("RUN Choose Task:[请输入括号内的数字]"))
        PrintUtils.print_delay(self.tips,0.001)
        return ChooseWithCategoriesTask.__choose(self.dic,self.tips,self.array,self.categories)


class FileUtils():
    @staticmethod
    def delete(path):
        if os.path.exists(path):
            result = CmdTask("sudo rm -rf {}".format(path),3).run()
            return result[0]==0
        return False

    @staticmethod
    def getbashrc():
        """
        优先home,没有home提供root
        """
        bashrc_result = CmdTask("ls /home/*/.bashrc", 0).run() 
        if bashrc_result[0]!=0:  bashrc_result = CmdTask("ls /root/.bashrc", 0).run()
        return bashrc_result[1]
        
    @staticmethod
    def get_shell():
        shell = os.environ.get('SHELL')
        if not shell:
            return 'sh'
        if 'bash' in shell:
            return 'bash'
        elif 'zsh' in shell:
            return 'zsh'
        else:
            return 'sh'

    @staticmethod
    def exists(path):
        if os.path.exists(path):
            return True
        else:
            return False


    @staticmethod
    def getusers():
        """
        优先获取有home目录的普通用户, 没有普通用户则返回root
        """
        users = []
        
        # 遍历 /etc/passwd 文件来获取用户名和UID
        with open('/etc/passwd', 'r') as passwd_file:
            for line in passwd_file:
                user_info = line.split(':')
                username = user_info[0]
                home_dir = user_info[5]
                uid = int(user_info[2])
                
                # 过滤出有home目录且UID大于等于1000的普通用户
                if home_dir.startswith('/home') and uid >= 1000:
                    users.append(username)
        
        users.append('root')
        return users
    
    @staticmethod
    def getusershome():
        """
        优先home,没有home提供root
        """
        users = FileUtils.getusers()
        user_homes = []
        for user in users:
            if user=='root':
                user_homes.append("/root")
            else:
                user_homes.append("/home/"+str(user)+"/")
        return user_homes

    @staticmethod
    def new(path,name=None,data=''):
        PrintUtils.print_info(tr.tr("创建文件:{}").format(path+name))
        if not os.path.exists(path):
            CmdTask("sudo mkdir -p {}".format(path),3).run()
        if name!=None:
            # 使用临时文件和sudo权限来创建受保护的文件
            # 修复：使用 uuid 生成唯一临时文件名，避免权限冲突
            import uuid
            temp_file = "/tmp/{}_{}".format(uuid.uuid4(), name)
            try:
                with open(temp_file, "w") as f:
                    f.write(data)
                CmdTask("sudo mv {} {}".format(temp_file, path+name), 3).run()
            finally:
                # 确保临时文件被清理
                if os.path.exists(temp_file):
                    os.remove(temp_file)
        return True
    
    @staticmethod
    def append(path,adddata=''):
        data = ""
        with open(path) as f:
            data = f.read()

        data  += "\n"+adddata
        with open(path,"w") as f:
            f.write(data)
        return True

    @staticmethod
    def find_replace(file,pattern,new):
        """
        查找和删除文件
        """
        is_file = True
        for root, dirs, files in os.walk(file):
            for f in files:
                is_file = False
                file_path = os.path.join(root, f)
                with open(file_path) as f:
                    data = f.read()
                    re_result = re.findall(pattern,data)
                    if re_result:
                        for key in re_result:
                            data = data.replace(key,new)
                        with open(file_path,"w") as f:
                            f.write(data)
            # 遍历所有的文件夹
            for d in dirs:
                os.path.join(root, d)
        if is_file:
            with open(file) as f:
                data = f.read()
            re_result = re.findall(pattern,data)
            if re_result:
                for key in re_result:
                    data = data.replace(key,new)
                with open(file,"w") as f:
                    f.write(data)

    @staticmethod
    def find_replace_sub(file,start,end,new):
        """
        查找和删除文件
        """
        is_file = True
        for root, dirs, files in os.walk(file):
            for f in files:
                is_file = False
                file_path = os.path.join(root, f)
                with open(file_path) as f:
                    data = f.read()
                    start_index = data.find(start)
                    end_index = data.find(end)
                    if start_index>0 and end_index>0:
                        data = data[:start_index]+data[end_index+len(end):]
                        with open(file_path,"w") as f:
                            f.write(data)
            # 遍历所有的文件夹
            for d in dirs:
                os.path.join(root, d)
        if is_file:
            with open(file) as f:
                data = f.read()
                start_index = data.find(start)
                end_index = data.find(end)
                if start_index>0 and end_index>0:
                    data = data[:start_index]+data[end_index+len(end):]
                    with open(file,"w") as f:
                        f.write(data)
                    
    @staticmethod
    def check_result(result, patterns:list):
        # 处理 result 如果其长度正好为 3
        if len(result) == 3:
            # 将 result[1] 和 result[2] 安全转换为字符串并拼接
            result = str(result[1]) + str(result[2])
        
        # 如果 result 是字符串，确保它是一个可迭代对象
        if isinstance(result, str):
            result = [result]
        
        # 遍历 result 中的每一行
        for line in result:
            line = str(line)  # 确保 line 是字符串
            # 对每个 pattern 进行检查
            for pattern in patterns:
                # 如果找到一个匹配
                if len(re.findall(pattern, line)) == 1:
                    return True  # 返回 True 表示匹配成功
        # 如果所有行和所有模式都未匹配，返回 False
        return False

class AptUtils():
    @staticmethod
    def checkapt():
        result = CmdTask('sudo apt update',100).run()
        if result[0]!=0:
            if FileUtils.check_result(result,['certificate','证书']):
                PrintUtils.print_warn(tr.tr("检测到发生证书校验错误{}，自动取消https校验，如有需要请手动删除：rm /etc/apt/apt.conf.d/99verify-peer.conf").format(result[2]))
                CmdTask('touch /etc/apt/apt.conf.d/99verify-peer.conf').run()
                CmdTask('echo  "Acquire { https::Verify-Peer false }" > /etc/apt/apt.conf.d/99verify-peer.conf').run()
                CmdTask("sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys F42ED6FBAB17C654",10).run()
                result = CmdTask('sudo apt update',100).run()
        if result[0]!=0:
            PrintUtils.print_warn(tr.tr("apt更新失败,后续程序可能会继续尝试...,{}").format(result[2]))
            return False
        return True

    @staticmethod
    def getArch():
        result = CmdTask("dpkg --print-architecture",2).run()
        arc = result[1][0].strip("\n")
        if arc=='armhf': arc = 'arm64'
        if result[0]==0: return arc
        PrintUtils.print_error(tr.tr("小鱼提示:自动获取系统架构失败...请手动选择"))
        # @TODO 提供架构选项 amd64,i386,arm
        return None
    
    @staticmethod
    def search_package(name,pattern,replace1="",replace2=""):
        result = CmdTask("sudo apt search {} ".format(name),20).run()
        if result[0]!=0: 
            PrintUtils.print_error(tr.tr("搜索不到任何{}相关的包").format(name))
            return None
        dic = {}
        for line in result[1]:
            temp = re.findall(pattern,line)      
            if len(temp)>0: dic[temp[0].replace(replace1,"").replace(replace2,"")] = temp[0]
        if len(dic)==0: return None
        return dic
    
    @staticmethod 
    def install_pkg(name,apt_tool="apt",auto_yes=True,os_command=False):
        dic = AptUtils().search_package(name,name)
        yes = ""
        if auto_yes: 
            yes="-y"
        
        cmd_result = None
        if dic:
            for key in dic.keys():
                cmd_result = CmdTask("sudo {} install {} {}".format(apt_tool,dic[key],yes), 0, os_command=os_command).run()
                if os_command==False:
                    if FileUtils.check_result(cmd_result,["apt --fix-broken install"]):
                        print(cmd_result)
                        CmdTask("sudo apt --fix-broken install -y", os_command=True).run()
                        cmd_result = CmdTask("sudo {} install {} {}".format(apt_tool,dic[key],yes), 0, os_command=os_command).run()
        else:
            PrintUtils.print_warn(tr.tr("没有找到包：{}").format(name))
        return cmd_result

    @staticmethod
    def install_pkg_check_dep(name):
        """
        安装并检查依赖问题
        """
        result = AptUtils.install_pkg(name)
        if result:
            # 自动同意安装一次
            AptUtils.install_pkg('aptitude')
            if FileUtils.check_result(result,['未满足的依赖关系','unmet dependencies']):
                result = AptUtils.install_pkg(name,apt_tool="aptitude", os_command = False, auto_yes=True)
            # 还不行让用户手动安装
            while FileUtils.check_result(result,['未满足的依赖关系','unmet dependencies']):
                # 尝试使用aptitude解决依赖问题
                PrintUtils.print_warn("============================================================")
                PrintUtils.print_delay(tr.tr("请注意我，检测你在安装过程中出现依赖问题，请在稍后选择解决方案（第一个解决方案不一定可以解决问题，如再遇到可以采用下一个解决方案）,即可解决"))
                input(tr.tr("确认了解上述情况，请输入回车继续安装"))
                result = AptUtils.install_pkg(name,apt_tool="aptitude", os_command = True, auto_yes=False)
                result = AptUtils.install_pkg(name,apt_tool="aptitude", os_command = False, auto_yes=True)
                
    @staticmethod
    def get_fast_url(urls,timeout=1.5):
        """
        遍历请求 urls 中的地址，按照从快到慢排序返回。
        参数:
        - urls (list): 要测试的 URL 列表。
        返回:
        - sorted_urls (list): 按照响应时间从快到慢排序的 URL 列表。
        """
        latencies = {}
        for url in urls:
            parsed_url = urlparse(url)
            host = parsed_url.netloc
            path = parsed_url.path
            try:
                # 记录开始时间
                start_time = time.time()
                # 创建连接并发送请求
                conn = http.client.HTTPSConnection(host, timeout=timeout)  # 使用 HTTPS 连接
                conn.request("GET", path)
                response = conn.getresponse()
                # 记录结束时间
                end_time = time.time()
                # 计算延时（以秒为单位）
                latency = end_time - start_time
                # 将延时保存到字典中
                latencies[url] = latency
                PrintUtils.print_success("- {}\t\t延时:{:.2f}s".format(url,latency))
                # 关闭连接
                conn.close()
            except Exception as e:
                # 如果请求失败，记录为 None 或者一个很大的延时
                # print("Error accessing {}: {}".format(url, e))
                PrintUtils.print_info("- {}\t\t超时".format(url))
                latencies[url] = float('inf')

        # 按照延时从小到大排序 URL
        sorted_urls = sorted(latencies, key=latencies.get)

        return sorted_urls



"""
定义基础任务
"""

class BaseTool():
    TYPE_INSTALL = 0
    TYPE_UNINSTALL = 1
    TYPE_CONFIG = 2
    def __init__(self,name,tool_type):
        self.osinfo = osversion

        self.name = name
        self.type = tool_type
        self.author = '小鱼'
        self.author_email = 'fishros@foxmail.com'

    def init(self):
        # 初始化部分
        PrintUtils.print_delay(tr.tr("欢迎使用{},本工具由作者{}提供").format(self.name,self.author))
    
    def run(self):
        # 运行该任务
        pass

    def uninit(self):
        # 接触初始化
        pass
        # PrintUtils.print_delay("一键安装已开源，欢迎给个star/提出问题/帮助完善：https://github.com/fishros/install/ ")

def run_tool_file(file,authorun=True):
    """运行工具文件，可以获取其他工具的对象"""
    import importlib
    tool = importlib.import_module(file.replace(".py","")).Tool()
    if not authorun: return tool
    if tool.init()==False: return False
    if tool.run()==False: return False
    if tool.uninit()==False: return False
    return tool

def run_tool_url(url,url_prefix):
    CmdTask("wget {} -O /tmp/fishinstall/tools/{} --no-check-certificate".format(url,url[url.rfind('/')+1:])).run()
    run_tool_file(url.replace(url_prefix,'').replace("/","."))

def download_tools(id,tools,url_prefix):
    # download tool 
    url = tools[id]['tool']
    url = os.path.join(url_prefix,url)
    CmdTask("wget {} -O /tmp/fishinstall/tools/{} --no-check-certificate".format(url,url[url.rfind('/')+1:])).run()
    # download dep 
    for dep in  tools[id]['dep']:
        url = tools[dep]['tool']
        url = os.path.join(url_prefix,url)
        CmdTask("wget {} -O /tmp/fishinstall/tools/{} --no-check-certificate".format(url,url[url.rfind('/')+1:])).run()

osarch = AptUtils.getArch()