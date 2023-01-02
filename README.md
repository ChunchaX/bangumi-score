# bangumi-score

> 获取 BiliBili 番剧的真实评分

## 用法



```text
bangumi-score.py [-h] [--user-agent USER_AGENT] [--short-reviews SHORT_REVIEWS] [--long-reviews LONG_REVIEWS]
                 [--level {CRITICAL,FATAL,ERROR,WARN,WARNING,INFO,DEBUG,NOTSET}] [--interval INTERVAL]
                 [--no-log-file]      
                 bangumi

positional arguments:
  bangumi               The ID of the bangumi

options:
  -h, --help            show this help message and exit
  --user-agent USER_AGENT
                        User agent
  --short-reviews SHORT_REVIEWS
                        Number of short reviews collected(-1 means all)
  --long-reviews LONG_REVIEWS
                        Number of long reviews collected(-1 means all)
  --level {CRITICAL,FATAL,ERROR,WARN,WARNING,INFO,DEBUG,NOTSET}
                        Log output level
  --interval INTERVAL   Interval between two requests
  --no-log-file         No bangumi-score.log file
```

## 示例

1. 克隆项目
    ```
    $ git clone https://github.com/ChunchaX/bangumi-score.git && cd bangumi-score
    ```
2. 设置并激活虚拟环境
    ```
    $  python -m venv . && ./Scripts/activate
    ```
3. 安装依赖
    ```
    $ pip install -r requirements.txt
    ```
4. 运行脚本（以番剧《三体》为例）
    ```
    $ python bangumi-score.py 4315402
    ```

## 许可证
[MIT License.](./LICENSE)
