mkdir -p /tmp/fishinstall/tools/translation/assets
wget http://mirror.fishros.com/install/install.py -O /tmp/fishinstall/install.py 2>>/dev/null 
source /etc/profile

SUDO=''
if [ $UID -ne 0 ];then
    SUDO='sudo'
fi
$SUDO apt install python3-distro python3-yaml -y
$SUDO python3 /tmp/fishinstall/install.py
$SUDO rm -rf /tmp/fishinstall/

if [ -f fishros ]; then
    $SUDO rm fishros
fi

# 初始假设默认是 Bash
shell_name='bash'
if shopt -u lastpipe 2> /dev/null; then
    # 当前 shell 是 Bash
    :
else
    # 当前 shell 是 Zsh 或其他 shell
    if test -n "$ZSH_VERSION"; then
        shell_name='zsh'
    else
        # 当前使用的 shell 不是 Bash 或 Zsh
        shell_name=''
    fi
fi

# 根据 shell 名称加载相应的配置文件
if [ "$shell_name" = "bash" ]; then
    if [ -f ~/.bashrc ]; then
        source ~/.bashrc
    fi
elif [ "$shell_name" = "zsh" ]; then
    if [ -f ~/.zshrc ]; then
        source ~/.zshrc
    fi
fi
