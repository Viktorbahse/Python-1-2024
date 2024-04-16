from PyQt5.QtCore import QObject, pyqtSignal
import time


class TimingSignal(QObject):
    time_updated = pyqtSignal(str)


TIMING_SIGNAL = TimingSignal()


def timeit(func):
    # Измеряет время выполнения функции, надо написать @timeit перед нужной функцией
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        work_time = (end_time - start_time) * 1000

        # Отправляет время через сигнал (он выше)
        TIMING_SIGNAL.time_updated.emit(f"{func.__name__} time: {work_time:.3f} ms")
        return result
    return wrapper
