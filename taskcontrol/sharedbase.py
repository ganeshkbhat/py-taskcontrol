# SHARED BASE

import time
import logging
from .interfaces import TimeBase, LogsBase, CommandBase


class UtilsBase():
    def validate_object(self, event_object, values=[]):
        keys = event_object.keys()
        if len(keys) == len(values):
            if type(values) == list:
                for k in values:
                    if k in keys:
                        return True
                    else:
                        return False
            elif type(values) == dict:
                v_keys = values.keys()
                for v in v_keys:
                    if v in keys:
                        for k in keys:
                            if type(values.get(v)) == type(event_object.get(k)):
                                continue
                            else:
                                return False
                    else:
                        return False
        return False


class ClosureBase():
    def class_closure(self, **kwargs):
        closure_val = kwargs

        def getter(key, value=None):
            if (type(value) == int and value == 1) or (type(value) == str and value == "1"):
                keys = closure_val[key]
                val = []
                for t in keys:
                    if t:
                        val.append(closure_val[key].get(t))
                return val
            elif type(value) == str:
                val = closure_val[key].get(value)
                if val:
                    return [val]
                return []
            elif type(value) == list:
                vl = []
                for tk in value:
                    if int(tk) == 1:
                        for i in closure_val[key].keys():
                            vl.append(closure_val[key].get(i))
                    elif tk in closure_val[key].keys():
                        vl.append(closure_val[key].get(tk))
                return vl
            return []

        def setter(key, value=None, inst=None):
            if type(value) == dict and inst != None:
                if inst.__class__.__name__ == "SharedBase":
                    closure_val[key].update({value.get("name"): value})
                elif value.get("workflow_kwargs").get("shared") == True:
                    inst.shared.setter(key, value, inst.shared)
                elif value.get("workflow_kwargs").get("shared") == False:
                    closure_val[key].update({value.get("name"): value})
                return True
            else:
                raise TypeError("Problem with " + key +
                                " Value setting " + str(value))

        def deleter(key, value=None):
            if type(value) == str:
                if value != None:
                    closure_val[key].pop(value)
                else:
                    raise TypeError("Problem with " + key +
                                    " Value deleting " + value)
                return True
            elif type(value) == int:
                if value == 1:
                    for v in value:
                        closure_val[key].pop(v)
                return True
            return False

        def log(config):
            pass

        def authenticate(config):
            pass

        def is_authenticated(config):
            pass

        def logout(config):
            pass

        return (getter, setter, deleter)


class SharedBase(ClosureBase):

    __instance = None

    def __init__(self):
        super().__init__()
        self.getter, self.setter, self.deleter = self.class_closure(
            tasks={}, ctx={}, plugins={}, config={}, workflow={}
        )
        if SharedBase.__instance != None:
            pass
        else:
            SharedBase.__instance = self

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(SharedBase, cls).__new__(cls)
        return cls.__instance

    @staticmethod
    def getInstance():
        if not SharedBase.__instance:
            return SharedBase()
        return SharedBase.__instance


class TimerBase(TimeBase, ClosureBase, UtilsBase):

    def __init__(self, options, timers={}):
        super()

        if not options and type(options) != dict:
            raise TypeError("Options not provided")

        self.getter, self.setter, self.deleter = self.class_closure(
            timers=timers)

    def time(self, options):

        # options object expected
        # {"name":"name", "logger": "", "format": ""}

        logger = options.get("logger")
        t = self.getter("timers", options.get("name"))

        if len(t) > 0:
            timer = t[0].perf_counter()
        else:
            raise TypeError(
                "Wrong timer name provided. No such timer or multiple names matched")

        if not timer:
            raise ValueError("Did not find timer")
        if logger:
            logger.log(timer)
        return timer


class LogBase(LogsBase, ClosureBase, UtilsBase):

    def __init__(self, name, config):

        self.getter, self.setter, self.deleter = self.class_closure(loggers={})

        # self.setter("loggers", config, self)
        # self.format = None
        # implement handlers and LoggerAdapters
        # self.handler = None
        # _del implementation fn (get from config)
        self._del = lambda x: x

        # delete implementation fn (get from config)
        self.delete = lambda x: x

    def create_logger(self, config):

        # Config object expected
        # { "name":"name", "logger":logger, "level": "debug", "format": "",
        #   "handlers": {"handler": "", "value": ""}, "handlers": [{"handler": "", "value": ""}] }

        logger = self.getter("loggers", config.get("name"))

        # Use config here
        # config contains network info if logging needed to network
        if len(logger) > 1:
            raise ValueError(
                "Number of logger items ({0}) incorrect. Check the logger registeration".format(len(logger)))
        elif len(logger) == 1:
            log = logger[0]
        else:
            log = logging.getLogger(config.get("name"))[0]

        if config.get("handlers") and type(config.get("handlers")) == list:
            for i in config.get("handlers"):
                # {"handler": "FileHandler", "value": None}
                h = getattr(logging, config.get(i["handler"]))(
                    config.get(i["value"]))
                h.setLevel(getattr(logging, config.get("level")))
                log.addHandler(h)
        elif config.get("handlers") and type(config.get("handlers")) == dict:
            h = getattr(logging, config.get("handler"))(config.get("value"))
            h.setLevel(getattr(logging, config.get("level")))
            log.addHandler(h)
        else:
            raise TypeError("Config object handler key error")

        log.setFormatter(log.Formatter(config.get("format")))
        config["logger"] = log
        self.setter("loggers", config, self)

    def delete_logger(self, options):

        # options object expected
        # {"key":"name", "value": ""}

        self.deleter(options.get("key"), options.get("value"))

    def log(self, options):
        # TODO: Concurrency can be added
        # https://docs.python.org/3/howto/logging-cookbook.html

        # options object expected
        # {"name":"name", "level": "debug", "message": ""}

        logger = self.getter("loggers", options.get("name"))
        if (not len(logger) == 0 or not len(logger) > 1) and logger:
            log = logger[0]
        else:
            raise ValueError(
                "Logger items ({0}) incorrect. Check logger".format(len(logger)))

        level = options.get("level")
        message = options.get("message")

        try:
            if level == "debug" and log:
                log.debug(message)
            if level == "info" and log:
                log.info(message)
            if level == "info" and log:
                log.warning(message)
            if level == "error" and log:
                log.error(message)
            if level == "critical" and log:
                log.critical(message)
            return True
        except Exception as e:
            log.raise_error(e, level, message)
            return False


class CommandsBase(CommandBase, ClosureBase, UtilsBase):
    
    def __init__(self, options, commands={}):
        self.getter, self.setter, self.deleter = self.class_closure(
            commands=commands)

    def create(self, config):
        pass
    
    def run(self, config):
        pass

    def close(self, config):
        pass
    
    def delete(self, config):
        pass
    

if __name__ == "__main__":
    l = LogBase("Test", {})


if __name__ == "__main__":
    t = TimerBase({}, {})


__all__ = [
    "SharedBase", "ClosureBase",
    "UtilsBase", "TimerBase",
    "LogBase", "CommandsBase"
]
