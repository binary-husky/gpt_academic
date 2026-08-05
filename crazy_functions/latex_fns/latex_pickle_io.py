import pickle


class SafeUnpickler(pickle.Unpickler):

    def get_safe_classes(self):
        from crazy_functions.latex_fns.latex_actions import LatexPaperFileGroup, LatexPaperSplit
        from crazy_functions.latex_fns.latex_toolbox import LinkedListNode
        from numpy.core.multiarray import scalar
        from numpy import dtype
        # 定义允许的安全类
        safe_classes = {
            # 在这里添加其他安全的类
            'LatexPaperFileGroup': LatexPaperFileGroup,
            'LatexPaperSplit': LatexPaperSplit,
            'LinkedListNode': LinkedListNode,
            'scalar': scalar,
            'dtype': dtype,
        }
        return safe_classes

    def find_class(self, module, name):
        # 只允许特定的类进行反序列化
        self.safe_classes = self.get_safe_classes()
        match_class_name = None
        for class_name in self.safe_classes.keys():
            if (class_name in f'{module}.{name}'):
                match_class_name = class_name
        if match_class_name is not None:
            return self.safe_classes[match_class_name]
        # 如果尝试加载未授权的类，则抛出异常
        raise pickle.UnpicklingError(f"Attempted to deserialize unauthorized class '{name}' from module '{module}'")

def objdump(obj, file="objdump.tmp"):

    with open(file, "wb+") as f:
        pickle.dump(obj, f)
    return


def objload(file="objdump.tmp"):
    import os

    if not os.path.exists(file):
        return
    with open(file, "rb") as f:
        unpickler = SafeUnpickler(f)
        return unpickler.load()
