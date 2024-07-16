from toolkit.fileutils import Fileutils
from toolkit.logger import Logger

O_FUTL = Fileutils()
S_DATA = "../data/"
F_SETG = S_DATA + "settings.yml"
if not O_FUTL.is_file_exists(F_SETG):
    O_FUTL.add_path(F_SETG)
    O_FUTL.copy_file()

logging = Logger(10)
settings = O_FUTL.get_lst_fm_yml(F_SETG)
perc = settings["perc"]
buff = settings["buff"]
secs = settings["secs"]
max_target = settings["max_target"]
perc_col_name = f"perc_gr_{int(perc)}"

CNFG = O_FUTL.get_lst_fm_yml("../../holdings_monitor.yml")
