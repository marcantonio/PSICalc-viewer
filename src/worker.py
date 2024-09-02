import traceback

from PySide6.QtCore import QRunnable, Signal, QObject


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.isCancelled = False

    def run(self):
        try:
            results = self.fn(*self.args, **self.kwargs)
            if not self.isCancelled:
                self.signals.result.emit(results)
        except Exception:
            self.signals.error.emit(traceback.format_exc())
        finally:
            if not self.isCancelled:
                self.signals.finished.emit()

    def cancel(self):
        self.isCancelled = True


class WorkerSignals(QObject):
    result = Signal(object)
    finished = Signal()
    error = Signal(str)
