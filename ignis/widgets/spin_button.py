from gi.repository import Gtk, GObject
from ignis.base_widget import BaseWidget

class SpinButton(Gtk.SpinButton, BaseWidget):
    """
    Bases: `Gtk.SpinButton <https://lazka.github.io/pgi-docs/#Gtk-4.0/classes/SpinButton.html>`_.

    A widget that allows the user to increment or decrement the displayed value within a specified range.

    Properties:
        - **min** (``float``, optional, read-write): Minimum value.
        - **max** (``float``, optional, read-write): Maximum value.
        - **step** (``float``, optional, read-write): Step increment.
        - **value** (``float``, optional, read-write): Current value.
        - **on_change** (``callable``, optional, read-write): Function to call when the value changes.

    .. code-block:: python

        Widget.SpinButton(
            min=0,
            max=100,
            step=1,
            value=50,
            on_change=lambda x, value: print(value)
        )
    """
    __gtype_name__ = "IgnisSpinButton"
    __gproperties__ = {**BaseWidget.gproperties}

    def __init__(self, min: int = None, max: int = None, **kwargs):
        Gtk.SpinButton.__init__(self)
        self._on_change = None
        self.adjustment = Gtk.Adjustment(
            value=0, lower=0, upper=100, step_increment=1, page_increment=0, page_size=0
        )
        self.min = min
        self.max = max
        BaseWidget.__init__(self, **kwargs)

        self.connect("value-changed", self.__invoke_on_change)

    @GObject.Property
    def value(self) -> float:
        return super().get_value()

    @value.setter
    def value(self, value: float) -> None:
        self.adjustment.set_value(value)

    @GObject.Property
    def min(self) -> float:
        return self.adjustment.props.lower

    @min.setter
    def min(self, value: float) -> None:
        self.adjustment.props.lower = value

    @GObject.Property
    def max(self) -> float:
        return self.adjustment.props.upper

    @max.setter
    def max(self, value: float) -> None:
        self.adjustment.props.upper = value

    @GObject.Property
    def step(self) -> float:
        return self.adjustment.props.step_increment

    @step.setter
    def step(self, value: float) -> None:
        self.adjustment.props.step_increment = value

    @GObject.Property
    def on_change(self) -> callable:
        return self._on_change

    @on_change.setter
    def on_change(self, value: callable) -> None:
        self._on_change = value

    def __invoke_on_change(self, *args) -> None:
        if self.on_change:
            self.on_change(self, self.value)
