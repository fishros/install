# -*- coding: utf-8 -*-
from .base import BaseTool

class Tool(BaseTool):
    def __init__(self):
        self.type = BaseTool.TYPE_INSTALL
        self.name = "模板工程"
        self.autor = '小鱼'

    def run(self):
        #正式的运行
        pass
