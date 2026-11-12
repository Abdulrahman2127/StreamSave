import sys


def restore_worker_streams():
    """Windowed PyInstaller executables need explicit access to redirected pipes."""
    if sys.platform != "win32":
        return
    import ctypes
    import io
    import msvcrt
    import os
    if sys.stderr is None:
        sys.stderr = open(os.devnull, "w", encoding="utf-8")
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.GetStdHandle.argtypes = [ctypes.c_ulong]
    kernel.GetStdHandle.restype = ctypes.c_void_p
    for name, handle_id, mode, flags in (
        ("stdin", -10, "rb", os.O_RDONLY),
        ("stdout", -11, "wb", os.O_WRONLY),
    ):
        if getattr(sys, name) is None:
            handle = kernel.GetStdHandle(handle_id & 0xFFFFFFFF)
            if not handle or handle == ctypes.c_void_p(-1).value:
                raise RuntimeError("Worker requires redirected input and output pipes.")
            fd = msvcrt.open_osfhandle(handle, flags | os.O_BINARY)
            stream = io.TextIOWrapper(os.fdopen(fd, mode), encoding="utf-8", write_through=True)
            setattr(sys, name, stream)


def main():
    if "--worker" in sys.argv:
        restore_worker_streams()
        from downloader.worker import run
        return run()
    from downloader.gui import Application
    app = Application()
    if "--smoke-test" in sys.argv:
        app.after(800, app.close)
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
