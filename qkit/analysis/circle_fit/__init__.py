import logging

import qkit

circle_fit_version = qkit.cfg.get("circle_fit_version", 1)

if circle_fit_version == 1:
    pass
elif circle_fit_version == 2:
    pass
else:
    logging.warning("Circle fit version not properly set in configuration!")
