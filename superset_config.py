
from flask_appbuilder.security.manager import AUTH_DB

# 认证类型 - 仍然使用 AUTH_DB 作为基础认证类型
AUTH_TYPE = AUTH_DB
# 自定义验证器
from superset.custom_security_manager import CustomSecurityManager
CUSTOM_SECURITY_MANAGER = CustomSecurityManager

# 外部系统的jwt secret ,用于自定义的验证器验证token
EXT_JWT_SECRET_KEY = "adg_crm_dev"
# 外部系统的用户需要存在这些角色中的一个，才具有superset的管理权限
EXT_SUPERSET_ADMIN_ROLES = ["超级管理员"]



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


# 语言配置
LANGUAGES = {
    "en": {"flag": "us", "name": "English"},
    "zh": {"flag": "cn", "name": "Chinese"},
    "zh_TW": {"flag": "tw", "name": "Traditional Chinese"},
    # 可以添加更多语言
}

BABEL_DEFAULT_LOCALE = "zh"