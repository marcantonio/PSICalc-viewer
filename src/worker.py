import traceback

from PySide6.QtCore import QThread, Signal, QObject


# This was a QRunnable and used with QThreadPool, but there's no way to forcable kill
# it. When reimplementing stop functionality in psicalc, this can be changed back to a
# QRunnable that checks for the cancel signal for cleaner shutdown
class Worker(QThread):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.isCancelled = False
        # Only required while this is a subclass of QThread
        self.setTerminationEnabled()

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
        self.terminate()
        self.isCancelled = True


class WorkerSignals(QObject):
    result = Signal(object)
    finished = Signal()
    error = Signal(str)
