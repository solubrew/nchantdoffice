# TODAY is 2026-08-17:
- the following issues were found to existing testing the NchantdOffice Desktop Application with all its most updated internal dependencies.

## Document Changes:
- add date/time insert button to NchantdOfficeScript document toolbar with ctrl+d hotkey
- fix node sorting to sort a starting _ to the top
- need to update Toolbox on node delete
- need to redirect to previous node on node delete / failback to sibling / failback to parent
- need to identify ways to speed up new document creation process
- fix NchantdOfficeMatrix to store entered values internally and restore when no external file has been opened
- deactivate NchantdOfficeMatrix formula entry in toolbar until 0.0.3


## Issues Found:



## Bugs:
2026-08-17 22:53:18,452 - micromole.storage                         587: INFO     - Get Table app_user {} db None
2026-08-17 22:53:18,452 - squirl.orgnql.sonql                       257: WARNING  - Table app_user
2026-08-17 22:53:18,453 - squirl.orgnql.sonql                       257: WARNING  - CMD PRAGMA table_info(app_user);
2026-08-17 22:53:18,453 - squirl.orgnql.sonql                       257: WARNING  - Table app_user
2026-08-17 22:53:18,454 - squirl.orgnql.sonql                       257: WARNING  - CMD SELECT [app_user_PK], [UUID], [mac_hash_txt], [user_nm_txt], [password_txt], [saltUUID], [iterations_txt], [address_txt], [public_key_txt], [is_private_bit], [is_secure_bit], [instance_FK], [CREBY_FK], [CREON_DTTM], [MODBY_FK], [MODON_DTTM], [DELETE_BIT], [ARCHIVE_BIT], [ACTIVE_BIT] FROM "app_user"   
 ORDER BY 7
2026-08-17 22:53:18,454 - micromole.storage                         597: INFO     - Data Empty DataFrame
Columns: [app_user_PK, UUID, mac_hash_txt, user_nm_txt, password_txt, saltUUID, iterations_txt, address_txt, public_key_txt, is_private_bit, is_secure_bit, instance_FK, CREBY_FK, CREON_DTTM, MODBY_FK, MODON_DTTM, DELETE_BIT, ARCHIVE_BIT, ACTIVE_BIT]
Index: []
2026-08-17 22:53:18,455 - nchantrs.utilities.users                  257: WARNING  - Using generated password for non-secure app - this should be replaced
2026-08-17 22:53:18,455 - nchantdoffice.models                      257: WARNING  - [models] bootstrap_app_user failed: 'NchantdUser' object has no attribute 'verify_password'
Traceback (most recent call last):
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 2111, in bootstrap_app_user
    self.store_app_user(user, db="db")
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 3484, in store_app_user
    payload = _build_app_user_payload(user)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 4637, in _build_app_user_payload
    payload["password_txt"] = _coerce_scalar(pword)
                              ^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/models.py", line 4623, in _coerce_scalar
    return _coerce_scalar(next(value))
                          ^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/utilities/users.py", line 102, in get_password
    if self.verify_password(password):
       ^^^^^^^^^^^^^^^^^^^^
AttributeError: 'NchantdUser' object has no attribute 'verify_password'. Did you mean: 'verify_pword'?
2026-08-17 22:53:18,457 - nchantdoffice.updates.db                   79: INFO     - Updating pyffice document
2026-08-17 22:53:23,476 - nchantdoffice.updates.checker             257: WARNING  - [update_checker] GET api/check-update failed: HTTPSConnectionPool(host='nchantdoffice.com', port=443): Max retries exceeded with url: /api/check-update?current_version=0.0.1&os=qt6-linux (Caused by ConnectTimeoutError(<HTTPSConnection(host='nchantdoffice.com', port=443) at 0x7057e8bd86b0>, 'Connection to nchantdoffice.com timed out. (connect timeout=5.0)'))
2026-08-17 22:53:23,476 - micromole.storage                         587: INFO     - Get Table vw_tab_document {'WHERE': {'IN': {'pid_txt': ['067ca837-17f6-74e7-8000-f7de9b7927f1'], 'tabset_type_txt': ['center']}}, 'ORDER': [5]} db None