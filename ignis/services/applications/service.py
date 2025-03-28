from gi.repository import Gio  # type: ignore
from ignis.base_service import BaseService
from .application import Application
from ignis.options import options
from ignis.gobject import IgnisProperty


class ApplicationsService(BaseService):
    """
    Provides a list of applications installed on the system.
    It also allows "pinning" of apps and retrieving a list of pinned applications.

    There are options available for this service: :class:`~ignis.options.Options.Applications`.

    Example usage:

    .. code-block:: python

        from ignis.services.applications import ApplicationsService

        applications = ApplicationsService.get_default()
        for i in applications.apps:
            print(i.name)

    """

    def __init__(self):
        super().__init__()
        self._apps: dict[str, Application] = {}
        self._pinned: dict[str, Application] = {}

        self._monitor = Gio.AppInfoMonitor.get()
        self._monitor.connect("changed", lambda x: self.__sync())

        self.__sync()

    @IgnisProperty
    def apps(self) -> list[Application]:
        """
        A list of all installed applications.
        """
        return sorted(self._apps.values(), key=lambda x: x.name)

    @IgnisProperty
    def pinned(self) -> list[Application]:
        """
        A list of all pinned applications.
        """
        return list(self._pinned.values())

    def __connect_entry(self, entry: Application) -> None:
        entry.connect("pinned", lambda x: self.__pin_entry(x))
        entry.connect("unpinned", lambda x: self.__unpin_entry(x))

    def __sync(self) -> None:
        self._apps = {}
        self._pinned = {}
        self.__read_pinned_apps()
        for app in Gio.AppInfo.get_all():
            if isinstance(app, Gio.DesktopAppInfo):
                self.__add_app(app)

        self.notify("apps")
        self.notify("pinned")

    def __add_app(self, app: Gio.DesktopAppInfo) -> None:
        if app.get_nodisplay():
            return

        if app.get_id() in self._pinned:
            entry = Application(app=app, is_pinned=True)
        else:
            entry = Application(app=app, is_pinned=False)

        self.__connect_entry(entry)
        self._apps[entry.id] = entry

    def __read_pinned_apps(self) -> None:
        for pinned in options.applications.pinned_apps:
            try:
                app = Gio.DesktopAppInfo.new(desktop_id=pinned)
            except TypeError:
                continue
            if not app:
                return

            entry = Application(app=app, is_pinned=True)
            self.__connect_entry(entry)
            self._pinned[entry.id] = entry

    def __sync_pinned(self) -> None:
        pinned_ids = [p.id for p in self.pinned]
        options.applications.pinned_apps = pinned_ids
        self.notify("pinned")

    def __pin_entry(self, entry: Application) -> None:
        self._pinned[entry.id] = entry
        self.__sync_pinned()

    def __unpin_entry(self, entry: Application) -> None:
        self._pinned.pop(entry.id)
        self.__sync_pinned()

    @classmethod
    def search(
        cls,
        apps: list[Application],
        query: str,
    ) -> list[Application]:
        """
        Search applications by a query.

        Args:
            apps: A list of applications where to search, e.g., :attr:`~ignis.services.applications.ApplicationsService.apps`.
            query: The string to be searched for.

        Returns:
            list[Application]: A list of applications filtered by the provided query.
        """
        return [
            entry
            for result in Gio.DesktopAppInfo.search(query)
            for entry in apps
            if entry.id in result
        ]
