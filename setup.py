
import setuptools


with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="autosend",  # 打包后生成的文件名，会以这个 name 为前缀
    version="0.0.1",  # 版本
    author="flish_wang",  # 作者
    author_email="flish_wang@sina.com",  # 作者邮箱
    description="a simple tool that logs what is printed on the screen, and emails the logs to you",
    long_description=long_description,  # 详细描述
    long_description_content_type="text/markdown",  # 详细描述的文本类型
    packages=setuptools.find_packages(),
    url="https://www.baidu.com",  # 项目地址

    # 配置元数据信息。更多内容参见：https://pypi.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 3 - Alpha",  # 项目开发阶段
        "Programming Language :: Python :: 3",  # 编程语言
        "License :: OSI Approved :: MIT License",  # license
        "Operating System :: OS Independent",  # 操作系统
    ],

    # 当前项目的依赖，比如当前项目依赖了 requests 库，当按照当前的模块时，会自动把 requests 也安装上
    install_requires=[
        "requests",
        # "pytest>=3.3.1",  # 也可以出依赖的具体版本
    ],

    package_data={"pipmodule": ["*.jpg", ]},  # package_data 可以将一些静态的包内的文件，打包进你的模块中，文件支持通配符的方式，如：{"package_name": ["*.txt", "*.jpg"]}

    python_requires=">=3"  # 设置当前项目适用的 python 版本：3，也可以写成支持多个版本的范围：">=2.7, <=3"
)
