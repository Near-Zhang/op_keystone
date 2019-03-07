class CustomException(Exception):
    """
    自定义异常类，修改了打印时的显示方式
    """
    code = 0

    def __message__(self):
        exception_message = self.args[0]
        exception_class = self.__class__.__name__
        return '%s: %s' %(exception_class, exception_message)


class PageNotFind(CustomException):
    """
    无法找到页面
    """
    def __init__(self, path):
        self.code = 404
        exception_message = 'path %s is not find' % path
        super().__init__(exception_message)


class InternalError(CustomException):
    """
    服务内部逻辑错误
    """
    def __init__(self):
        self.code = 500
        exception_message = 'there was an internal error'
        super().__init__(exception_message)


class MethodNotAllowed(CustomException):
    """
    请求的方法不被允许
    """
    def __init__(self, method, path):
        self.code = 405
        exception_message = 'method %s is not allowed by path %s' % (method, path)
        super().__init__(exception_message)


class LoginFailed(CustomException):
    """
    登录失败
    """
    def __init__(self):
        self.code = 403
        exception_message = 'user does not exist or password is error'
        super().__init__(exception_message)


class CredenceInvalid(CustomException):
    """
    校验凭证无效
    """
    def __init__(self, empty=False, refresh=False):
        self.code = 403
        exception_message = 'the access token in the header is invalid'
        if empty:
            exception_message = 'the access token in the header is required'
        elif refresh:
            exception_message = 'the refresh token is invalid'
        super().__init__(exception_message)


class PermissionDenied(CustomException):
    """
    权限被拒绝
    """
    def __init__(self):
        self.code = 403
        exception_message = 'unable to access the server'
        super().__init__(exception_message)


class PasswordError(CustomException):
    """
    密码错误
    """
    def __init__(self):
        self.code = 403
        exception_message = 'password is error'
        super().__init__(exception_message)


class PasswordInvalid(CustomException):
    """
    密码内容不符合有效标准
    """
    def __init__(self, exception):
        self.code = 400
        exception_message = exception.__str__()
        super().__init__(exception_message)


class RoutingParamsError(CustomException):
    """
    路由的资源 uuid 参数有错误
    """
    def __init__(self):
        self.code = 400
        exception_message = 'the res uuid of routing params is missing'
        super().__init__(exception_message)


class RequestParamsError(CustomException):
    """
    从请求中提取的参数有错误
    """
    def __init__(self, empty=False, not_json=False, opt=None, invalid=None):
        self.code = 400
        if empty:
            exception_message = ''
        elif not_json:
            exception_message = 'request params is not a standard json'
        elif opt and not invalid:
            exception_message = 'the %s of request params is missing or none' % opt
        elif opt and invalid:
            exception_message = 'the %s of request params is not in range' % opt
        else:
            exception_message = 'request params is not in the correct content type'
        super().__init__(exception_message)


class ObjectNotExist(CustomException):
    """
    模型中不存在查找的对象
    """
    def __init__(self, model):
        self.code = 404
        exception_message = 'objects does not exist in the model %s' % model
        super().__init__(exception_message)


class DatabaseError(CustomException):
    """
    数据库进行对象保存操作时的错误
    """
    def __init__(self, msg, model):
        self.code = 409
        exception_message = '%s in the model %s' % (msg.lower(), model)
        super().__init__(exception_message)


class RequestError(CustomException):
    """
    对后端请求 api 错误
    """
    def __init__(self, method, url):
        self.code = 502
        exception_message = 'the response of %s %s is not available' % (method, url)
        super().__init__(exception_message)


class ResponseBackendError(CustomException):
    """
    对后端请求 api 返回的响应错误
    """
    def __init__(self, method, url, message):
        self.code = 500
        exception_message = 'the response of %s %s is %s' % (method, url, message)
        super().__init__(exception_message)