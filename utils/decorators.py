from functools import wraps
from src.services.auth_service import AuthService

def require_valid_token(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        token = getattr(self.current_user, "token", None)

        if not isinstance(token, str):
            return func(self, *args, **kwargs)

        from src.controllers.auth_controller import AuthController
        auth_ctrl = AuthController(self.session, self.base_view, self.current_user, self.history)

        if not token:
            return auth_ctrl.show_expired_token_popup()

        payload = AuthService.verify_token(token)
        if payload is None:
            return auth_ctrl.show_expired_token_popup()

        return func(self, *args, **kwargs)
    return wrapper