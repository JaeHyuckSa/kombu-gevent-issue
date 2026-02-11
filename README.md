# kombu-gevent-issue (issue-2463)

> `ignore_errors()` does not catch gevent's `ConcurrentObjectUseError` during connection close, causing Celery worker crash

## Test

```bash
./tls/generate.sh
docker compose up --build reproduce
```

## Test Result

```
[1] Transport.connection_errors:
    amqp.exceptions.ConnectionError
    builtins.OSError
    ConcurrentObjectUseError included? False

[2] Connecting to AMQPS broker...
    Connected via <gevent.ssl.SSLSocket ...>

[3] Greenlet A: blocking read on SSL socket
[4] Greenlet B: connection.close() → SSL read for CloseOk

    ConcurrentObjectUseError: This socket is already used by another greenlet: ...

[5] ignore_errors() does NOT catch ConcurrentObjectUseError:
    BUG: propagated (not caught)
```
