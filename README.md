# 2dfan 自动签到

~基于 git action 的自动签到~

本地部署的2DFan签到脚本

## 安装

### 编译

使用以下指令进行编译：
```
pip install pyinstaller
pyinstaller --onefile --noconsole --clean main.py
```

### 用户区分/人机验证

设置 config.json, 示例：
```
{
    "sessions": {
        "葉月けいか": {
            "id": 12345,
            "auth": "%2BQ0*************"
        }
    },
    "ez_captcha": "fd1d*************""
}
```

这里使用了 ez-captcha.com 的 api 作为案例，通过人机验证

### 开机启动

为编译好后的`main.exe`创建一个快捷方式，将快捷方式放入Windows的启动文件夹中

## 补充说明

有能力的话，请支持2dfan的运营，这一项目更多是用来学习尝试的
