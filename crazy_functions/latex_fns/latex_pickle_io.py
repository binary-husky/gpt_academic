import pickle


class SafeUnpickler(pickle.Unpickler):

    def get_safe_classes(self):
        from .latex_actions import LatexPaperFileGroup, LatexPaperSplit
        # 定义允许的安全类
        safe_classes = {
            # 在这里添加其他安全的类
            'LatexPaperFileGroup': LatexPaperFileGroup,
            'LatexPaperSplit' : LatexPaperSplit,
        }
        return safe_classes

    def find_class(self, module, name):
        # 只允许特定的类进行反序列化
        self.safe_classes = self.get_safe_classes()
        if f'{module}.{name}' in self.safe_classes:
            return self.safe_classes[f'{module}.{name}']
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
