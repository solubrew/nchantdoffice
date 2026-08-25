



# Bugs:
- 2026-08-25 09:30:34,799 - nchantdoffice.utilities.user_config       118: INFO     - [user_config] loaded XDG config from /home/solubrew/.config/nchantdoffice/config.yaml
2026-08-25 09:30:34,800 - __main__                                  138: INFO     - Start
2026-08-25 09:30:34,800 - __main__                                  115: INFO     - Removal Complete
2026-08-25 09:30:34,800 - nchantrs.nchantrs                          53: INFO     - Begin Nchantment
2026-08-25 09:30:34,800 - nchantrs.nchantrs                          63: INFO     - Configuring Qt Environment for NchantdOffice
2026-08-25 09:30:34,800 - nchantrs.nchantrs                          65: INFO     - Qt Environment Configured
2026-08-25 09:30:36,043 - micromole.storage                         498: INFO     - Disconnecting MicroStash...
2026-08-25 09:30:36,048 - micromole.storage                         585: INFO     - Get Table vw_app_instance {} db None
2026-08-25 09:30:36,060 - nchantdoffice.nchantdoffice                54: INFO     - NchantdOfficeCloak: {'path': '<[user_home]>/.config/<[application_NCD]>/config.yaml', 'requires_auth': True, 'has_agents': True, 'has_comms': True, 'has_services': True, 'has_extensions': True, 'has_library': True, 'version': '0.0.0'}
2026-08-25 09:30:36,060 - nchantdoffice.nchantdoffice               240: INFO     - NchantdOfficeMainWindow init: parent=NchantdOfficeCloak
2026-08-25 09:30:36,583 - micromole.storage                         498: INFO     - Disconnecting MicroStash...
2026-08-25 09:30:38,065 - nchantdoffice.utilities.config            120: INFO     - [config] PyfficeApplicationConfig.__init__: section dicts initialised
2026-08-25 09:30:38,065 - micromole.storage                         498: INFO     - Disconnecting MicroStash...
2026-08-25 09:30:38,068 - nchantdoffice.views                        43: INFO     - NchantdOfficeCloakView init: parent=NchantdOfficeCloak
2026-08-25 09:30:38,071 - micromole.storage                         585: INFO     - Get Table vw_app_instance {} db None
nchantdoffice.license.startup_refresh WARNING startup_refresh: could not write entitlement_stale=True to preferences_db: 'dict' object has no attribute 'set'
2026-08-25 09:30:39,668 - nchantdoffice.license.startup_refresh - WARNING - startup_refresh: could not write entitlement_stale=True to preferences_db: 'dict' object has no attribute 'set'
nchantdoffice.license.startup_refresh ERROR startup_refresh: bootstrap failed (Cannot connect to host api.nchantdoffice.com:443 ssl:default [Name or service not known]); cannot continue
Traceback (most recent call last):
  File "/home/solubrew/ENVs/nchantrs/lib/python3.12/site-packages/aiohttp/connector.py", line 1574, in _create_direct_connection
    hosts = await self._resolve_host(host, port, traces=traces)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/solubrew/ENVs/nchantrs/lib/python3.12/site-packages/aiohttp/connector.py", line 1190, in _resolve_host
    return await asyncio.shield(resolved_host_task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/solubrew/ENVs/nchantrs/lib/python3.12/site-packages/aiohttp/connector.py", line 1221, in _resolve_host_with_throttle
    addrs = await self._resolver.resolve(host, port, family=self._family)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/solubrew/ENVs/nchantrs/lib/python3.12/site-packages/aiohttp/resolver.py", line 40, in resolve
    infos = await self._loop.getaddrinfo(
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/asyncio/base_events.py", line 901, in getaddrinfo
    return await self.run_in_executor(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/concurrent/futures/thread.py", line 58, in run
    result = self.fn(*self.args, **self.kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/socket.py", line 963, in getaddrinfo
    for res in _socket.getaddrinfo(host, port, family, type, proto, flags):
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
socket.gaierror: [Errno -2] Name or service not known

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/license/startup_refresh.py", line 240, in refresh_if_needed
    bootstrap_body = license_remote.sync_bootstrap(
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/license/remote.py", line 537, in sync_bootstrap
    return asyncio.run(self.bootstrap(*args, **kwargs))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/asyncio/runners.py", line 194, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/asyncio/base_events.py", line 687, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/license/remote.py", line 352, in bootstrap
    status, body = await self._http_post(self._BOOTSTRAP_PATH, payload)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/license/remote.py", line 570, in _http_post
    async with session.post(
  File "/home/solubrew/ENVs/nchantrs/lib/python3.12/site-packages/aiohttp/client.py", line 1521, in __aenter__
    self._resp: _RetType = await self._coro
                           ^^^^^^^^^^^^^^^^
  File "/home/solubrew/ENVs/nchantrs/lib/python3.12/site-packages/aiohttp/client.py", line 788, in _request
    resp = await handler(req)
           ^^^^^^^^^^^^^^^^^^
  File "/home/solubrew/ENVs/nchantrs/lib/python3.12/site-packages/aiohttp/client.py", line 742, in _connect_and_send_request
    conn = await self._connector.connect(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/solubrew/ENVs/nchantrs/lib/python3.12/site-packages/aiohttp/connector.py", line 672, in connect
    proto = await self._create_connection(req, traces, timeout)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/solubrew/ENVs/nchantrs/lib/python3.12/site-packages/aiohttp/connector.py", line 1251, in _create_connection
    _, proto = await self._create_direct_connection(req, traces, timeout)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/solubrew/ENVs/nchantrs/lib/python3.12/site-packages/aiohttp/connector.py", line 1580, in _create_direct_connection
    raise ClientConnectorDNSError(req.connection_key, exc) from exc
aiohttp.client_exceptions.ClientConnectorDNSError: Cannot connect to host api.nchantdoffice.com:443 ssl:default [Name or service not known]
2026-08-25 09:30:39,668 - nchantdoffice.license.startup_refresh - ERROR - startup_refresh: bootstrap failed (Cannot connect to host api.nchantdoffice.com:443 ssl:default [Name or service not known]); cannot continue
Traceback (most recent call last):
  File "/home/solubrew/ENVs/nchantrs/lib/python3.12/site-packages/aiohttp/connector.py", line 1574, in _create_direct_connection
    hosts = await self._resolve_host(host, port, traces=traces)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/solubrew/ENVs/nchantrs/lib/python3.12/site-packages/aiohttp/connector.py", line 1190, in _resolve_host
    return await asyncio.shield(resolved_host_task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/solubrew/ENVs/nchantrs/lib/python3.12/site-packages/aiohttp/connector.py", line 1221, in _resolve_host_with_throttle
    addrs = await self._resolver.resolve(host, port, family=self._family)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/solubrew/ENVs/nchantrs/lib/python3.12/site-packages/aiohttp/resolver.py", line 40, in resolve
    infos = await self._loop.getaddrinfo(
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/asyncio/base_events.py", line 901, in getaddrinfo
    return await self.run_in_executor(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/concurrent/futures/thread.py", line 58, in run
    result = self.fn(*self.args, **self.kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/socket.py", line 963, in getaddrinfo
    for res in _socket.getaddrinfo(host, port, family, type, proto, flags):
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
socket.gaierror: [Errno -2] Name or service not known

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/license/startup_refresh.py", line 240, in refresh_if_needed
    bootstrap_body = license_remote.sync_bootstrap(
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/license/remote.py", line 537, in sync_bootstrap
    return asyncio.run(self.bootstrap(*args, **kwargs))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/asyncio/runners.py", line 194, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/asyncio/base_events.py", line 687, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/license/remote.py", line 352, in bootstrap
    status, body = await self._http_post(self._BOOTSTRAP_PATH, payload)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/license/remote.py", line 570, in _http_post
    async with session.post(
  File "/home/solubrew/ENVs/nchantrs/lib/python3.12/site-packages/aiohttp/client.py", line 1521, in __aenter__
    self._resp: _RetType = await self._coro
                           ^^^^^^^^^^^^^^^^
  File "/home/solubrew/ENVs/nchantrs/lib/python3.12/site-packages/aiohttp/client.py", line 788, in _request
    resp = await handler(req)
           ^^^^^^^^^^^^^^^^^^
  File "/home/solubrew/ENVs/nchantrs/lib/python3.12/site-packages/aiohttp/client.py", line 742, in _connect_and_send_request
    conn = await self._connector.connect(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/solubrew/ENVs/nchantrs/lib/python3.12/site-packages/aiohttp/connector.py", line 672, in connect
    proto = await self._create_connection(req, traces, timeout)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/solubrew/ENVs/nchantrs/lib/python3.12/site-packages/aiohttp/connector.py", line 1251, in _create_connection
    _, proto = await self._create_direct_connection(req, traces, timeout)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/solubrew/ENVs/nchantrs/lib/python3.12/site-packages/aiohttp/connector.py", line 1580, in _create_direct_connection
    raise ClientConnectorDNSError(req.connection_key, exc) from exc
aiohttp.client_exceptions.ClientConnectorDNSError: Cannot connect to host api.nchantdoffice.com:443 ssl:default [Name or service not known]
Traceback (most recent call last):
  File "/home/solubrew/ENVs/nchantrs/lib/python3.12/site-packages/aiohttp/connector.py", line 1574, in _create_direct_connection
    hosts = await self._resolve_host(host, port, traces=traces)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/solubrew/ENVs/nchantrs/lib/python3.12/site-packages/aiohttp/connector.py", line 1190, in _resolve_host
    return await asyncio.shield(resolved_host_task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/solubrew/ENVs/nchantrs/lib/python3.12/site-packages/aiohttp/connector.py", line 1221, in _resolve_host_with_throttle
    addrs = await self._resolver.resolve(host, port, family=self._family)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/solubrew/ENVs/nchantrs/lib/python3.12/site-packages/aiohttp/resolver.py", line 40, in resolve
    infos = await self._loop.getaddrinfo(
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/asyncio/base_events.py", line 901, in getaddrinfo
    return await self.run_in_executor(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/concurrent/futures/thread.py", line 58, in run
    result = self.fn(*self.args, **self.kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/socket.py", line 963, in getaddrinfo
    for res in _socket.getaddrinfo(host, port, family, type, proto, flags):
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
socket.gaierror: [Errno -2] Name or service not known

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/solubrew/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/cmds/runNchantdOffice.py", line 139, in <module>
    run(argv)
  File "/home/solubrew/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/cmds/runNchantdOffice.py", line 132, in run
    nchantment("NchantdOffice", args, app, cfg, wizard)
  File "/mnt/iverse/SB/3_Functions/Operations/opENGRg/3_Work/jobElfSys/actvPython/tskNchantrs/1_DELTA/nchantrs/nchantrs/nchantrs.py", line 66, in nchantment
    app = main_app(name, instance, None, cfg, args)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/nchantdoffice.py", line 59, in __init__
    self.view = NchantdOfficeCloakView(self)
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/views.py", line 75, in __init__
    startup_refresh.refresh_if_needed(
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/license/startup_refresh.py", line 240, in refresh_if_needed
    bootstrap_body = license_remote.sync_bootstrap(
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/license/remote.py", line 537, in sync_bootstrap
    return asyncio.run(self.bootstrap(*args, **kwargs))
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/asyncio/runners.py", line 194, in run
    return runner.run(main)
           ^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/asyncio/base_events.py", line 687, in run_until_complete
    return future.result()
           ^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/license/remote.py", line 352, in bootstrap
    status, body = await self._http_post(self._BOOTSTRAP_PATH, payload)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/mnt/iverse/SB/3_Functions/Projects/NchantdOffice/3_Work/1_DELTA/nchantdoffice/nchantdoffice/license/remote.py", line 570, in _http_post
    async with session.post(
  File "/home/solubrew/ENVs/nchantrs/lib/python3.12/site-packages/aiohttp/client.py", line 1521, in __aenter__
    self._resp: _RetType = await self._coro
                           ^^^^^^^^^^^^^^^^
  File "/home/solubrew/ENVs/nchantrs/lib/python3.12/site-packages/aiohttp/client.py", line 788, in _request
    resp = await handler(req)
           ^^^^^^^^^^^^^^^^^^
  File "/home/solubrew/ENVs/nchantrs/lib/python3.12/site-packages/aiohttp/client.py", line 742, in _connect_and_send_request
    conn = await self._connector.connect(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/solubrew/ENVs/nchantrs/lib/python3.12/site-packages/aiohttp/connector.py", line 672, in connect
    proto = await self._create_connection(req, traces, timeout)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/solubrew/ENVs/nchantrs/lib/python3.12/site-packages/aiohttp/connector.py", line 1251, in _create_connection
    _, proto = await self._create_direct_connection(req, traces, timeout)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/solubrew/ENVs/nchantrs/lib/python3.12/site-packages/aiohttp/connector.py", line 1580, in _create_direct_connection
    raise ClientConnectorDNSError(req.connection_key, exc) from exc
aiohttp.client_exceptions.ClientConnectorDNSError: Cannot connect to host api.nchantdoffice.com:443 ssl:default [Name or service not known]
2026-08-25 09:30:40,303 - micromole.storage                         498: INFO     - Disconnecting MicroStash...