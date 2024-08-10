import os
from tools.base import CmdTask
from tools.base import FileUtils
result = CmdTask("ls /opt/ros/*/setup.bash", 0).run()
shellrc_result = CmdTask("ls /root/.bashrc", 0).run()
print(result)
print(shellrc_result)
