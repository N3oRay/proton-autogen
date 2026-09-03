#!/usr/bin/env python3

"""
system_tray.py

Implémentation minimale d'un StatusNotifierItem (SNI) via D-Bus.

Cette classe n'utilise ni GTK3, ni AppIndicator, ni Gtk.StatusIcon.
Elle fonctionne donc indépendamment de GTK4.

Le bureau doit toutefois fournir un watcher/host StatusNotifierItem
pour afficher effectivement l'icône dans sa zone système.

API publique :

    tray = SystemTray(
        icon_name="proton-autogen",
        title="Proton Autogen",
        on_activate=callback,
    )

    tray.start()

    ...

    tray.stop()
"""

from __future__ import annotations

import asyncio
import logging
import threading
from typing import Callable, Optional

from dbus_next import BusType, Message, MessageType
from dbus_next.aio import MessageBus
from dbus_next.service import ServiceInterface, method, dbus_property, signal
from dbus_next.constants import PropertyAccess

logger = logging.getLogger(__name__)


SNI_INTERFACE = "org.kde.StatusNotifierItem"
SNI_OBJECT_PATH = "/StatusNotifierItem"
SNI_BUS_NAME = "org.proton_autogen.StatusNotifierItem"


class StatusNotifierItem(ServiceInterface):
    """
    Interface D-Bus org.kde.StatusNotifierItem.

    Implémentation volontairement minimale :
      - Status
      - Category
      - Id
      - Title
      - IconName
      - ToolTip
      - Activate()
      - ContextMenu()
      - NewIcon
      - NewTitle
      - NewToolTip
    """

    def __init__(
        self,
        icon_name: str,
        title: str,
        on_activate: Optional[Callable[[], None]] = None,
    ):
        super().__init__("org.kde.StatusNotifierItem")

        self._icon_name = icon_name
        self._title = title
        self._on_activate = on_activate

    # ------------------------------------------------------------------
    # Propriétés SNI
    # ------------------------------------------------------------------

    @dbus_property(PropertyAccess.READ)
    def Category(self) -> "s":
        return "ApplicationStatus"

    @dbus_property(PropertyAccess.READ)
    def Id(self) -> "s":
        return "proton-autogen"

    @dbus_property(PropertyAccess.READ)
    def Title(self) -> "s":
        return self._title

    @dbus_property(PropertyAccess.READ)
    def Status(self) -> "s":
        return "Active"

    @dbus_property(PropertyAccess.READ)
    def IconName(self) -> "s":
        return self._icon_name

    @dbus_property(PropertyAccess.READ)
    def IconPixmap(self) -> "a(iiay)":
        # On utilise IconName plutôt qu'un pixmap.
        return []

    @dbus_property(PropertyAccess.READ)
    def OverlayIconName(self) -> "s":
        return ""

    @dbus_property(PropertyAccess.READ)
    def AttentionIconName(self) -> "s":
        return ""

    @dbus_property(PropertyAccess.READ)
    def AttentionIconPixmap(self) -> "a(iiay)":
        return []

    @dbus_property(PropertyAccess.READ)
    def AttentionMovieName(self) -> "s":
        return ""

    @dbus_property(PropertyAccess.READ)
    def ToolTip(self) -> "(sa(iiay)ss)":
        return (
            self._icon_name,
            [],
            self._title,
            "",
        )

    # ------------------------------------------------------------------
    # Signaux
    # ------------------------------------------------------------------

    @signal()
    def NewIcon(self) -> "":
        return

    @signal()
    def NewTitle(self) -> "":
        return

    @signal()
    def NewToolTip(self) -> "":
        return

    # ------------------------------------------------------------------
    # Méthodes SNI
    # ------------------------------------------------------------------

    @method()
    def Activate(self, x: "i", y: "i"):
        logger.debug("System tray Activate(%s, %s)", x, y)

        if self._on_activate is not None:
            self._on_activate()

    @method()
    def ContextMenu(self, x: "i", y: "i"):
        logger.debug("System tray ContextMenu(%s, %s)", x, y)

    @method()
    def SecondaryActivate(self, x: "i", y: "i"):
        logger.debug(
            "System tray SecondaryActivate(%s, %s)",
            x,
            y,
        )

        if self._on_activate is not None:
            self._on_activate()

    @method()
    def Scroll(self, delta: "i", orientation: "s"):
        logger.debug(
            "System tray Scroll(delta=%s, orientation=%s)",
            delta,
            orientation,
        )


class SystemTray:
    """
    Gestionnaire haut niveau du StatusNotifierItem.

    L'API est volontairement simple pour pouvoir être utilisée depuis
    DashboardMiniMixin sans que celui-ci connaisse D-Bus.

    Exemple :

        tray = SystemTray(
            title="Proton Autogen",
            icon_name="proton-autogen",
            on_activate=restore_window,
        )

        tray.start()

        ...

        tray.stop()
    """

    def __init__(
        self,
        title: str = "Proton Autogen",
        icon_name: str = "proton-autogen",
        on_activate: Optional[Callable[[], None]] = None,
    ):
        self.title = title
        self.icon_name = icon_name
        self.on_activate = on_activate

        self._thread: Optional[threading.Thread] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None

        self._bus: Optional[MessageBus] = None
        self._sni: Optional[StatusNotifierItem] = None

        self._started = threading.Event()
        self._stopped = threading.Event()

    # ------------------------------------------------------------------
    # API publique
    # ------------------------------------------------------------------

    def start(self) -> None:
        """
        Démarre le StatusNotifierItem dans son propre thread.

        Cette méthode ne bloque pas le thread GTK principal.
        """

        if self._thread is not None:
            return

        self._stopped.clear()

        self._thread = threading.Thread(
            target=self._thread_main,
            name="proton-autogen-system-tray",
            daemon=True,
        )

        self._thread.start()

        if not self._started.wait(timeout=5):
            logger.warning(
                "StatusNotifierItem: démarrage D-Bus non confirmé"
            )

    def stop(self) -> None:
        """
        Arrête proprement le StatusNotifierItem.
        """

        loop = self._loop

        if loop is not None and loop.is_running():
            loop.call_soon_threadsafe(
                lambda: asyncio.create_task(self._async_stop())
            )

        thread = self._thread

        if thread is not None:
            thread.join(timeout=2)

        self._thread = None
        self._loop = None

    # ------------------------------------------------------------------
    # Thread asyncio / D-Bus
    # ------------------------------------------------------------------

    def _thread_main(self) -> None:
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)

        try:
            self._loop.run_until_complete(
                self._async_start()
            )

            self._started.set()

            self._loop.run_forever()

        except Exception:
            logger.exception(
                "Erreur dans le thread StatusNotifierItem"
            )

        finally:
            try:
                self._loop.run_until_complete(
                    self._async_cleanup()
                )
            except Exception:
                logger.exception(
                    "Erreur pendant le nettoyage du StatusNotifierItem"
                )

            self._loop.close()
            self._stopped.set()

    async def _async_start(self) -> None:
        self._bus = await MessageBus(
            bus_type=BusType.SESSION
        ).connect()

        self._sni = StatusNotifierItem(
            icon_name=self.icon_name,
            title=self.title,
            on_activate=self._activate_from_dbus,
        )

        self._bus.export(
            SNI_OBJECT_PATH,
            self._sni,
        )

        await self._bus.request_name(
            SNI_BUS_NAME
        )

        await self._register_with_status_notifier_watcher()

        logger.info(
            "StatusNotifierItem démarré: %s",
            SNI_BUS_NAME,
        )

    async def _async_cleanup(self) -> None:
        if self._bus is None:
            return

        try:
            self._bus.unexport(
                SNI_OBJECT_PATH
            )
        except Exception:
            pass

        try:
            self._bus.disconnect()
        except Exception:
            pass

        self._bus = None
        self._sni = None

    async def _async_stop(self) -> None:
        logger.debug("Arrêt du StatusNotifierItem")

        await self._async_cleanup()

        if self._loop is not None:
            self._loop.stop()

    # ------------------------------------------------------------------
    # Enregistrement auprès du watcher SNI
    # ------------------------------------------------------------------

    async def _register_with_status_notifier_watcher(self) -> None:
        """
        Recherche un StatusNotifierWatcher puis enregistre notre SNI.

        KDE fournit normalement ce watcher.

        D'autres environnements peuvent le fournir également.
        """

        if self._bus is None:
            return

        watcher_name = (
            "org.kde.StatusNotifierWatcher"
        )

        watcher_path = (
            "/StatusNotifierWatcher"
        )

        watcher_interface = (
            "org.kde.StatusNotifierWatcher"
        )

        try:
            message = Message(
                destination=watcher_name,
                path=watcher_path,
                interface=watcher_interface,
                member="RegisterStatusNotifierItem",
                signature="s",
                body=[
                    SNI_BUS_NAME,
                ],
            )

            reply = await self._bus.call(message)

            if reply.message_type == MessageType.ERROR:
                logger.warning(
                    "Impossible d'enregistrer le StatusNotifierItem: %s",
                    reply.body,
                )
                return

            logger.info(
                "StatusNotifierItem enregistré auprès du watcher"
            )

        except Exception as exc:
            logger.warning(
                "Aucun StatusNotifierWatcher disponible: %s",
                exc,
            )

    # ------------------------------------------------------------------
    # Callback
    # ------------------------------------------------------------------

    def _activate_from_dbus(self) -> None:
        """
        Appelé lorsqu'un utilisateur clique sur l'icône.

        Le callback utilisateur est exécuté depuis le thread D-Bus.
        Le Dashboard doit donc repasser sur le thread GTK si nécessaire.
        """

        if self.on_activate is None:
            return

        try:
            self.on_activate()
        except Exception:
            logger.exception(
                "Erreur dans le callback SystemTray.on_activate"
            )
