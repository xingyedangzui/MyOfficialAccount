# -*- coding: utf-8 -*-
# filename: main.py
import web
import consts
from handle import Handle


def fixed_group(seq, size):
    """
    修复 web.py 在 Python 3.7+ 中的 StopIteration 问题
    """

    def take(seq, n):
        for _ in range(n):
            try:
                yield next(seq)
            except StopIteration:
                return

    it = iter(seq)
    while True:
        x = list(take(it, size))
        if len(x) == 0:
            break
        yield x


# 替换原有的 group 函数
web.utils.group = fixed_group

urls = (
    '/wx',
    'Handle',
)

if __name__ == '__main__':
    app = web.application(urls, globals())
    # 指定端口80，便于生产环境部署
    # web.py使用系统参数来指定端口
    import sys

    sys.argv = ['main.py', consts.HOST]
    app.run()
