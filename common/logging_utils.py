import logging
from rich.logging import RichHandler

def setup_logger(name: str, logfile: str | None = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Console
    if not any(isinstance(h, RichHandler) for h in logger.handlers):
        ch = RichHandler(rich_tracebacks=True, show_time=True)
        ch.setLevel(logging.INFO)
        logger.addHandler(ch)

    # Arquivo
    if logfile:
        fh = logging.FileHandler(logfile, encoding="utf-8")
        fh.setLevel(logging.INFO)
        fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger