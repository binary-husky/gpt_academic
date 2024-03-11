import platform
import pickle
import multiprocessing

def run_in_subprocess_wrapper_func(v_args):
    func, args, kwargs, return_dict, exception_dict = pickle.loads(v_args)
    import sys
    try:
        result = func(*args, **kwargs)
        return_dict['result'] = result
    except Exception as e:
        exc_info = sys.exc_info()
        exception_dict['exception'] = exc_info

def run_in_subprocess_with_timeout(func, timeout=60):
    if platform.system() == 'Linux':
        def wrapper(*args, **kwargs):
            return_dict = multiprocessing.Manager().dict()
            exception_dict = multiprocessing.Manager().dict()
            v_args = pickle.dumps((func, args, kwargs, return_dict, exception_dict))
            process = multiprocessing.Process(target=run_in_subprocess_wrapper_func, args=(v_args,))
            process.start()
            process.join(timeout)
            if process.is_alive():
                process.terminate()
                raise TimeoutError(f'功能单元{str(func)}未能在规定时间内完成任务')
            process.close()
            if 'exception' in exception_dict:
                # ooops, the subprocess ran into an exception
                exc_info = exception_dict['exception']
                raise exc_info[1].with_traceback(exc_info[2])
            if 'result' in return_dict.keys():
                # If the subprocess ran successfully, return the result
                return return_dict['result']
        return wrapper
    else:
        return func