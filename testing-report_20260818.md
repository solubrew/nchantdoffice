# TODAY is 2026-08-18:
- the following issues were found to existing testing the NchantdOffice Desktop Application with all its most updated internal dependencies.

## Document Changes:

## Issues Found:
## Bugs:
2026-08-18 12:34:01,486 - nchantrs.widgets.widgets                  549: INFO     - Left Click
2026-08-18 12:34:01,778 - nchantrs.widgets.widgets                  499: INFO     - Focus Out
Traceback (most recent call last):
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/controls/buttons.py", line 162, in <lambda>
    self.clicked.connect(lambda checked: self.on_click(checked, handler, params))
                                         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/widgets/controls/buttons.py", line 154, in on_click
    handler(signal, params)
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/widgets/documents/media/scripts.py", line 349, in cmd_open_local_file
    raise Exception(f"local_file is None: {self.local_file}")
Exception: local_file is None: None
2026-08-18 12:34:05,309 - nchantrs.widgets.widgets                  494: INFO     - Focus In
2026-08-18 12:34:12,788 - nchantrs.widgets.widgets                  499: INFO     - Focus Out





2026-08-18 13:11:40,340 - nchantdoffice.models                      257: WARNING  - [models] bootstrap_app_user failed: 'NchantdUser' object has no attribute 'verify_password'
Traceback (most recent call last):
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 2110, in bootstrap_app_user
    self.store_app_user(user, db="db")
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 3483, in store_app_user
    payload = _build_app_user_payload(user)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 4636, in _build_app_user_payload
    payload["password_txt"] = _coerce_scalar(pword)
                              ^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 4622, in _coerce_scalar
    return _coerce_scalar(next(value))
                          ^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/utilities/users.py", line 102, in get_password
    if self.verify_password(password):
       ^^^^^^^^^^^^^^^^^^^^
AttributeError: 'NchantdUser' object has no attribute 'verify_password'. Did you mean: 'verify_pword'?
2026-08-18 13:11:40,342 - nchantdoffice.updates.db                   79: INFO     - Updating pyffice document