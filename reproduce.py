from gevent import monkey
monkey.patch_all()

import gevent
import amqp
import logging
import ssl

from kombu.common import ignore_errors
from kombu import Connection
from kombu.transport.pyamqp import Transport

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def demonstrate():
    ca_cert = "/tls/ca-cert.pem"

    from gevent._gevent_c_hub_primitives import ConcurrentObjectUseError

    logger.info("=" * 60)
    logger.info("ConcurrentObjectUseError not in Transport.connection_errors")
    logger.info("=" * 60)

    logger.info("\n[1] Transport.connection_errors:")
    for err in Transport.connection_errors:
        logger.info("    %s.%s", err.__module__, err.__name__)
    logger.info("    ConcurrentObjectUseError included? %s", ConcurrentObjectUseError in Transport.connection_errors)

    logger.info("\n[2] Connecting to AMQPS broker...")
    conn = amqp.Connection(
        host="rabbitmq:5671",
        userid="guest",
        password="guest",
        ssl={"ca_certs": ca_cert, "cert_reqs": ssl.CERT_REQUIRED},
    )
    conn.connect()
    conn.channel()
    logger.info("    Connected via %s", conn.transport.sock)

    logger.info("\n[3] Greenlet A: blocking read on SSL socket")
    errors = []

    def reader():
        try:
            conn.drain_events(timeout=30)
        except Exception as e:
            errors.append(e)

    g = gevent.spawn(reader)
    gevent.sleep(0.1)

    logger.info("[4] Greenlet B: connection.close() → SSL read for CloseOk")
    try:
        conn.close()
    except ConcurrentObjectUseError as e:
        logger.error("\n    ConcurrentObjectUseError: %s", e)
    except Exception as e:
        logger.error("\n    %s: %s", type(e).__name__, e)

    g.kill()
    gevent.sleep(0.1)

    logger.info("\n[5] ignore_errors() does NOT catch ConcurrentObjectUseError:")
    kombu_conn = Connection(
        "amqps://guest:guest@rabbitmq:5671//",
        ssl={"ca_certs": ca_cert, "cert_reqs": ssl.CERT_REQUIRED},
    )
    kombu_conn.connect()
    try:
        ignore_errors(kombu_conn, lambda: (_ for _ in ()).throw(
            ConcurrentObjectUseError("This socket is already used by another greenlet")
        ))
        logger.error("    BUG: silently passed (not caught)")
    except ConcurrentObjectUseError:
        logger.error("    BUG: propagated (not caught)")
    finally:
        try:
            kombu_conn.close()
        except Exception:
            pass

    logger.info("\n[6] In Celery, this causes worker crash:")
    logger.info("    events._close() → ignore_errors(c, dispatcher.connection.close)")
    logger.info("    → ConcurrentObjectUseError propagates → 'Unrecoverable error'")
    logger.info("\n" + "=" * 60)


if __name__ == "__main__":
    demonstrate()
