class ExceptionHandlerRegistry:
    '''
    This class allows to register exception handlers created for different module. When exception occurs it will check
    the origin of the exception and run proper handler.
    '''
    exception_handlers = {}

    @classmethod
    def register_exception_handler(cls, module_name, exception_handler):
        cls.exception_handlers[module_name] = exception_handler

    @classmethod
    def get_exception_handler(cls, module_name):
        return cls.exception_handlers.get(module_name)
