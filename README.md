# Superset (修改版)

这是 [Apache Superset](https://github.com/apache/superset) 的修改版本。

## 修改内容
- 增加默认的 `superset_config.py` 配置
- 增加中文翻译文件支持
- 增加自定义的验证器

原项目相关链接：
- 官方仓库：https://github.com/apache/superset
- 官方文档：https://superset.apache.org
- 中文文档：https://superset.org.cn


----

## docker 启动

```
docker-compose -f docker-compose-image-tag.yml down -v
docker-compose -f docker-compose-image-tag.yml up -d
```

### 注意事项

docker启动时，由于国内网络环境问题，需要设置superset-init的一些网络环境，参考如下 

```
  superset-init:
    image: *superset-image
    container_name: superset_init
    command: ["/app/docker/docker-init.sh"]
    env_file:
      - path: docker/.env # default
        required: true
      - path: docker/.env-local # optional override
        required: false
    depends_on:
      db:
        condition: service_started
      redis:
        condition: service_started
    user: "root"
    volumes: *superset-volumes
    healthcheck:
      disable: true
    environment:
      SUPERSET_LOAD_EXAMPLES: "no" 
      SUPERSET_LOG_LEVEL: "${SUPERSET_LOG_LEVEL:-info}"
      BABEL_DEFAULT_LOCALE: "zh"
      PIP_TRUSTED_HOST: "pypi.org pypi.python.org files.pythonhosted.org"
      PIP_DISABLE_PIP_VERSION_CHECK: "1"
      PIP_NO_CACHE_DIR: "1"
      PIP_INDEX_URL: "https://pypi.tuna.tsinghua.edu.cn/simple"
    dns:
      - 8.8.8.8
      - 8.8.4.4
```

## 修改配置信息

修改配置信息有两种方式

1. 直接修改主配置文件 superset/config.py 
2. 新增一个配置文件 superset_config.py, 并设置环境变量 SUPERSET_CONFIG_PATH 指向该文件，superset_config.py 中的配置会覆盖原有的config.py，可以只设置需要修改的配置项


### 启用语言选择

**注意**  如果是直接用`apachesuperset.docker.scarf.sh/apache/superset`的镜像，一般来说，启用语言选择就可以了，但如果是使用本地代码编译的镜像，它默认是没有前端需要的语言包数据的，还需要使用  `npm run build-translation` 来生成语言配置文件，然后再编译


superset的默认配置是没有多语言的，需要修改一个配置

```
# 启用语言选择
LANGUAGES = {
    "en": {"flag": "us", "name": "English"},
    "zh": {"flag": "cn", "name": "Chinese"},
    "zh_TW": {"flag": "tw", "name": "Traditional Chinese"},
    # 可以添加更多语言
}

```

这样就可以在superset后台修改语言


### 允许superset 仪表板的markdown组件引用 iframe 标签显示外部网页信息

```

HTML_SANITIZATION_SCHEMA_EXTENSIONS = {
    "tagNames": ["iframe"],
    "attributes": {
        "iframe": ["src", "width", "height", "frameborder", "allowfullscreen", "style", "sandbox", "allow"]
    }
}

```

### 允许superset图表联动

```
  FEATURE_FLAGS = {
    "DASHBOARD_NATIVE_FILTERS": True,
    "DASHBOARD_NATIVE_FILTERS_SET": True,
    "DASHBOARD_CROSS_FILTERS": True, 
    "HORIZONTAL_FILTER_BAR": True // 是否支持横向过滤器展示
  }
```


## dashboards等接口访问以及仪表板嵌入第三方系统

整体的逻辑是：获得仪表板的访问权限需要调用接口 `http://api/v1/security/guest_token/` 获取guest_token ，然后配合superset提供的前端npm包`@superset-ui/embedded-sdk`去嵌入仪表盘，但调用guest_token这个接口需要先获得登录的access_token 和 csrf_token ，并**使用cookie保持回话**，因此，关键接口为：

* `/api/v1/security/login`
* `/api/v1/security/csrf_token/`
* `/api/v1/security/guest_token/`

然后实际上获取到登录信息后，可以调用任意的接口，例如 
* `/api/v1/dashboard/` 接口可以获取目前所有的仪表板列表 （可以用于在外部系统获取当前可用的仪表板列表）
* `/api/v1/dashboard/{id_or_slug}/embedded` 接口可以设置或者获取嵌入的uuid（可以用于在外部系统根据上方的仪表板列表接口，开启仪表板的嵌入功能）

### 详细步骤如下

#### 1. 增加配置

开启guest_token以及设置相关角色
```
# Embedded config options
GUEST_ROLE_NAME = "CRMRead" 
# GUEST_ROLE_NAME = "Public" # 为什么不使用这个角色，因为guest_token使用时，需要对角色提前设置can read dashboard ， can read charts 之类的角色，然后如果赋予Public角色这两项权限之后，可能是因为Public角色权限会覆盖Admin还是什么原因，导致 `/api/v1/dashboard/` 获取不到数据，因此我额外创建了个角色，然后赋予权限
GUEST_TOKEN_JWT_SECRET = "EySCCLqcibbpodYX2X7nNa/V1wsMPQ+1DnBMWh3t9JMa7iCpkkpY2y2L"  # noqa: S105
GUEST_TOKEN_JWT_ALGO = "HS256"  # noqa: S105
GUEST_TOKEN_HEADER_NAME = "X-GuestToken"  # noqa: S105
GUEST_TOKEN_JWT_EXP_SECONDS = 300  # 5 minutes
# Guest token audience for the embedded superset, either string or callable
GUEST_TOKEN_JWT_AUDIENCE = None
PUBLIC_ROLE_LIKE_GAMMA = False
```
开启嵌入权限
```
FEATURE_FLAGS = { "EMBEDDED_SUPERSET": True }
```
防止嵌入时的跨域问题（这两个配置是完全开放权限的，这不是一个最好的配置，理论上存在一些安全问题，可以详细查查这里面的配置）
```
ENABLE_CORS = True
TAISMAN_ENABLED = False
```


#### 2. 获取权限，依次调用接口获取guest_token 

1. `/api/v1/security/login`
2. `/api/v1/security/csrf_token/`
3. `/api/v1/security/guest_token/` 

对应的参数可以查看接口文档：[superset-api-doc](https://superset.apache.org/docs/api/)


### 注意事项（这些都是血泪经验）：
* 不管是调用`/api/v1/security/guest_token/` 还是调用 `/api/v1/dashboard/` 等接口，除了使用access_token和csrf_token外，都需要使用cookie保持回话，否则会报权限错误
* 不要给GUEST_ROLE_NAME配置Public角色，应另外添加一个CanRead之类的角色，单独给guest_token使用
* guest_token的嵌入，除了在接口给此token指定的资源访问权限外，还需要给他对应的角色赋予 can read Dashboard 和 can read chart 的权限，有的图表不属于chart，那么可以根据控制台的错误信息，酌情添加权限，例如 can explore json 
* `/api/v1/dashboard/{id_or_slug}/embedded` 这接口post时，可以开启某个dashboard的嵌入，此时传入的domain参数，是**不支持*号匹配**的（如果传入星号，无法匹配成功，嵌入的iframe会报403），需要设置具体嵌入仪表板的外部系统的url，例如：http://localhost:8000




## 启动后端开发环境 

先在根目录添加一个开发配置文件`superset_config.py`

```
# 嵌入相关的配置

FEATURE_FLAGS = {"ALERT_REPORTS": True, "EMBEDDED_SUPERSET": True, "HORIZONTAL_FILTER_BAR": True}
ENABLE_CORS = True
TALISMAN_ENABLED = False 

GUEST_ROLE_NAME = "CRMRead"
GUEST_TOKEN_JWT_SECRET = "test-guest-secret-change-me"  # noqa: S105
GUEST_TOKEN_JWT_ALGO = "HS256"  # noqa: S105
GUEST_TOKEN_HEADER_NAME = "X-GuestToken"  # noqa: S105
GUEST_TOKEN_JWT_EXP_SECONDS = 300  # 5 minutes

# 关于如何在仪表板嵌入 iframe 
HTML_SANITIZATION_SCHEMA_EXTENSIONS = {
    "tagNames": ["iframe"],
    "attributes": {
        "iframe": ["src", "width", "height", "frameborder", "allowfullscreen", "style", "sandbox", "allow"]
    }
}

# 关于在外部系统嵌入管理端
HTTP_HEADERS= {}
WTF_CSRF_ENABLED = False
ENABLE_CORS = True
CORS_OPTIONS = {
    'supports_credentials': True,
    'allow_headers': ['*'],
    'resources': ['*'],
    'origins': ['*']
}


APP_NAME = "CRM-BI" # 这个是嵌入系统时，显示的名称
ENABLE_PROXY_FIX = True # 启用代理修复功能（用于处理反向代理环境中的头）


SECRET_KEY = "SNcaNIWrWitz5hxnxolSXCKmO049ba8qUSAws3DQ8Som2KmAe7gxZy+x"
SUPERSET_SECRET_KEY = "SNcaNIWrWitz5hxnxolSXCKmO049ba8qUSAws3DQ8Som2KmAe7gxZy+x"

```

```
python -m venv venv  # 创建虚拟环境
source venv/bin/activate  # 激活虚拟环境

sudo apt-get install build-essential libssl-dev libffi-dev python3-dev python3-pip libsasl2-dev libldap2-dev default-libmysqlclient-dev pkg-config

pip install -r requirements/base.txt  # 安装依赖
pip install -r requirements/development.txt  # 安装依赖
pip install -r requirements/translations.txt  # 安装依赖


## 设置 Flask 应用
export FLASK_APP=superset
```

首次初始化数据库

最简单的，启用 SQLite
```
# 初始化数据库
superset db upgrade

# 创建管理员用户
superset fab create-admin

# 初始化角色和权限
superset init

# 加载示例数据（可选）
superset load-examples

# 在启动superset之前，还需要先编译前端项目
cd superset-frontend 
# 用pnpm好像容易成功点
pnpm i 
pnpm run build 

# 启动 Superset
superset run -p 8089 --with-threads --reload --debugger


```

可以增加一个快捷启动方式

```
dev-server:
	# Activate virtual environment, set config path, generate secret key, and run Superset
	. venv/bin/activate && \
	export SUPERSET_CONFIG_PATH=$(PWD)/superset_config.py && \
	export FLASK_APP=superset && \
	superset run -p 8089 --with-threads --reload --debugger

dev-frontend:
	cd superset-frontend; npm run dev-server
```

---

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/license/apache-2-0)
[![Latest Release on Github](https://img.shields.io/github/v/release/apache/superset?sort=semver)](https://github.com/apache/superset/releases/latest)
[![Build Status](https://github.com/apache/superset/actions/workflows/superset-python-unittest.yml/badge.svg)](https://github.com/apache/superset/actions)
[![PyPI version](https://badge.fury.io/py/apache_superset.svg)](https://badge.fury.io/py/apache_superset)
[![Coverage Status](https://codecov.io/github/apache/superset/coverage.svg?branch=master)](https://codecov.io/github/apache/superset)
[![PyPI](https://img.shields.io/pypi/pyversions/apache_superset.svg?maxAge=2592000)](https://pypi.python.org/pypi/apache_superset)
[![Get on Slack](https://img.shields.io/badge/slack-join-orange.svg)](http://bit.ly/join-superset-slack)
[![Documentation](https://img.shields.io/badge/docs-apache.org-blue.svg)](https://superset.apache.org)

<picture width="500">
  <source
    width="600"
    media="(prefers-color-scheme: dark)"
    src="https://superset.apache.org/img/superset-logo-horiz-dark.svg"
    alt="Superset logo (dark)"
  />
  <img
    width="600"
    src="https://superset.apache.org/img/superset-logo-horiz-apache.svg"
    alt="Superset logo (light)"
  />
</picture>