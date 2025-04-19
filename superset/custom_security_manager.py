
import logging
import jwt
import time
from superset.security.manager import SupersetSecurityManager
from flask_login import login_user
from flask import current_app

logger = logging.getLogger(__name__)

class CustomSecurityManager(SupersetSecurityManager):
    """
    自定义安全管理器，支持通过url参数传递token进行认证
    """
    def __init__(self, appbuilder):
        super().__init__(appbuilder)
        logger.info("CustomSecurityManager initialized")

    def request_loader(self, request):
        logger.info("CustomSecurityManager.request_loader called")
        # 从url参数中获取 token
        token = request.args.get('token')
        if token:
            try:
                # 从配置中获取JWT密钥
                jwt_secret_key = current_app.config.get('EXT_JWT_SECRET_KEY')
                if not jwt_secret_key:
                    logger.warning("EXT_JWT_SECRET_KEY not configured in Superset config")
                    return super().request_loader(request)

                # 验证token
                try:
                    # 使用标准JWT验证（这会验证jwt的格式和签名，以及是否已经过期）
                    payload = jwt.decode(token, jwt_secret_key, algorithms=['HS256'])
                    logger.info(f"JWT token validated successfully: {payload}")

                    # 检查JWT角色是否存在于配置的管理员角色中
                    admin_roles = current_app.config.get('EXT_SUPERSET_ADMIN_ROLES', [])
                    user_roles = payload.get('withRolesName', [])

                    # 检查用户角色是否与管理员角色有交集
                    has_admin_role = any(role in admin_roles for role in user_roles)

                    if not has_admin_role:
                        logger.warning(f"User does not have any admin roles. User roles: {user_roles}, Admin roles: {admin_roles}")
                        return None

                    logger.info(f"User has admin role. Proceeding with login.")

                    # 找一个id=1的superset用户当做管理员登录
                    admin_user = self.get_session.query(self.user_model).filter_by(id=1).first()
                    if admin_user:
                        logger.info(f"Using default admin user: {admin_user.username} with id {admin_user.id}")
                        login_user(admin_user, remember=True)
                        return admin_user

                except jwt.InvalidTokenError as e:
                    logger.warning(f"Invalid JWT token: {e}")
                    return None

            except Exception as e:
                logger.exception(f"Error during token validation: {e}")

        return super().request_loader(request)

