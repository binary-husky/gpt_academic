from __future__ import annotations

import warnings

from gradio_client.documentation import document, set_documentation_group

from gradio.blocks import BlockContext
from gradio.events import Changeable, Selectable

set_documentation_group("layout")


@document()
class Floating(BlockContext):
    """
    Floating is a layout element within Blocks that renders all children in absolute screen space.
    Example:
        with gr.Blocks() as demo:
            with gr.Floating():
                gr.Image("lion.jpg", scale=2)
                gr.Image("tiger.jpg", scale=1)
        demo.launch()
    Guides: controlling-layout
    """

    def __init__(
        self,
        *,
        variant: str = "default",
        visible: bool = True,
        init_x: str | None = "0%",
        init_y: str | None = "0%",
        width: str | None = "10%",
        drag: str | None = "everywhere",
        elem_id: str | None = None,
        elem_classes: list[str] | str | None = None,
        equal_height: bool = True,
        **kwargs,
    ):
        """
        Parameters:
            drag: how the floating element can be dragged. Can be 'everywhere', 'forbidden', or 'top'.
            variant: floating type, 'default' (no background), 'panel' (gray background color and rounded corners), or 'compact' (rounded corners and no internal gap).
            visible: If False, floating will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
            elem_classes: An optional string or list of strings that are assigned as the class of this component in the HTML DOM. Can be used for targeting CSS styles.
            equal_height: If True, makes every child element have equal height
        """
        self.variant = variant
        self.init_x = init_x
        self.init_y = init_y
        self.width = width
        self.drag = drag
        self.equal_height = equal_height
        if variant == "compact":
            self.allow_expected_parents = False
        BlockContext.__init__(
            self, visible=visible, elem_id=elem_id, elem_classes=elem_classes, **kwargs
        )

    def get_config(self):
        return {
            "type": "floating",
            "variant": self.variant,
            "init_x": self.init_x,
            "init_y": self.init_y,
            "width": self.width,
            "drag": self.drag,
            **super().get_config(),
        }

    @staticmethod
    def update(
        visible: bool | None = None,
    ):
        return {
            "visible": visible,
            "__type__": "update",
        }

    def style(
        self,
        *,
        equal_height: bool | None = None,
        **kwargs,
    ):
        """
        Styles the Floating.
        Parameters:
            equal_height: If True, makes every child element have equal height
        """
        if equal_height is not None:
            self.equal_height = equal_height
        return self


@document()
class Row(BlockContext):
    """
    Row is a layout element within Blocks that renders all children horizontally.
    Example:
        with gr.Blocks() as demo:
            with gr.Row():
                gr.Image("lion.jpg")
                gr.Image("tiger.jpg")
        demo.launch()
    Guides: controlling-layout
    """

    def __init__(
        self,
        *,
        variant: str = "default",
        visible: bool = True,
        elem_id: str | None = None,
        **kwargs,
    ):
        """
        Parameters:
            variant: row type, 'default' (no background), 'panel' (gray background color and rounded corners), or 'compact' (rounded corners and no internal gap).
            visible: If False, row will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
        """
        self.variant = variant
        if variant == "compact":
            self.allow_expected_parents = False
        super().__init__(visible=visible, elem_id=elem_id, **kwargs)

    def get_config(self):
        return {"type": "row", "variant": self.variant, **super().get_config()}

    @staticmethod
    def update(
        visible: bool | None = None,
    ):
        return {
            "visible": visible,
            "__type__": "update",
        }

    def style(
        self,
        *,
        equal_height: bool | None = None,
        mobile_collapse: bool | None = None,
        **kwargs,
    ):
        """
        Styles the Row.
        Parameters:
            equal_height: If True, makes every child element have equal height
            mobile_collapse: DEPRECATED.
        """
        if equal_height is not None:
            self._style["equal_height"] = equal_height
        if mobile_collapse is not None:
            warnings.warn("mobile_collapse is no longer supported.")
        return self


@document()
class Column(BlockContext):
    """
    Column is a layout element within Blocks that renders all children vertically. The widths of columns can be set through the `scale` and `min_width` parameters.
    If a certain scale results in a column narrower than min_width, the min_width parameter will win.
    Example:
        with gr.Blocks() as demo:
            with gr.Row():
                with gr.Column(scale=1):
                    text1 = gr.Textbox()
                    text2 = gr.Textbox()
                with gr.Column(scale=4):
                    btn1 = gr.Button("Button 1")
                    btn2 = gr.Button("Button 2")
    Guides: controlling-layout
    """

    def __init__(
        self,
        *,
        scale: int = 1,
        min_width: int = 320,
        variant: str = "default",
        visible: bool = True,
        elem_id: str | None = None,
        **kwargs,
    ):
        """
        Parameters:
            scale: relative width compared to adjacent Columns. For example, if Column A has scale=2, and Column B has scale=1, A will be twice as wide as B.
            min_width: minimum pixel width of Column, will wrap if not sufficient screen space to satisfy this value. If a certain scale value results in a column narrower than min_width, the min_width parameter will be respected first.
            variant: column type, 'default' (no background), 'panel' (gray background color and rounded corners), or 'compact' (rounded corners and no internal gap).
            visible: If False, column will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
        """
        self.scale = scale
        self.min_width = min_width
        self.variant = variant
        if variant == "compact":
            self.allow_expected_parents = False
        super().__init__(visible=visible, elem_id=elem_id, **kwargs)

    def get_config(self):
        return {
            "type": "column",
            "variant": self.variant,
            "scale": self.scale,
            "min_width": self.min_width,
            **super().get_config(),
        }

    @staticmethod
    def update(
        variant: str | None = None,
        visible: bool | None = None,
    ):
        return {
            "variant": variant,
            "visible": visible,
            "__type__": "update",
        }


class Tabs(BlockContext, Changeable, Selectable):
    """
    Tabs is a layout element within Blocks that can contain multiple "Tab" Components.
    """

    def __init__(
        self,
        *,
        selected: int | str | None = None,
        visible: bool = True,
        elem_id: str | None = None,
        **kwargs,
    ):
        """
        Parameters:
            selected: The currently selected tab. Must correspond to an id passed to the one of the child TabItems. Defaults to the first TabItem.
            visible: If False, Tabs will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
        """
        BlockContext.__init__(self, visible=visible, elem_id=elem_id, **kwargs)
        Changeable.__init__(self)
        Selectable.__init__(self)
        self.selected = selected

    def get_config(self):
        return {"selected": self.selected, **super(BlockContext, self).get_config()}

    @staticmethod
    def update(
        selected: int | str | None = None,
    ):
        return {
            "selected": selected,
            "__type__": "update",
        }


@document()
class Tab(BlockContext, Selectable):
    """
    Tab (or its alias TabItem) is a layout element. Components defined within the Tab will be visible when this tab is selected tab.
    Example:
        with gr.Blocks() as demo:
            with gr.Tab("Lion"):
                gr.Image("lion.jpg")
                gr.Button("New Lion")
            with gr.Tab("Tiger"):
                gr.Image("tiger.jpg")
                gr.Button("New Tiger")
    Guides: controlling-layout
    """

    def __init__(
        self,
        label: str,
        *,
        id: int | str | None = None,
        elem_id: str | None = None,
        **kwargs,
    ):
        """
        Parameters:
            label: The visual label for the tab
            id: An optional identifier for the tab, required if you wish to control the selected tab from a predict function.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
        """
        BlockContext.__init__(self, elem_id=elem_id, **kwargs)
        Selectable.__init__(self)
        self.label = label
        self.id = id

    def get_config(self):
        return {
            "label": self.label,
            "id": self.id,
            **super(BlockContext, self).get_config(),
        }

    def get_expected_parent(self) -> type[Tabs]:
        return Tabs

    def get_block_name(self):
        return "tabitem"


TabItem = Tab


class Group(BlockContext):
    """
    Group is a layout element within Blocks which groups together children so that
    they do not have any padding or margin between them.
    Example:
        with gr.Group():
            gr.Textbox(label="First")
            gr.Textbox(label="Last")
    """

    def __init__(
        self,
        *,
        visible: bool = True,
        elem_id: str | None = None,
        **kwargs,
    ):
        """
        Parameters:
            visible: If False, group will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
        """
        super().__init__(visible=visible, elem_id=elem_id, **kwargs)

    def get_config(self):
        return {"type": "group", **super().get_config()}

    @staticmethod
    def update(
        visible: bool | None = None,
    ):
        return {
            "visible": visible,
            "__type__": "update",
        }


@document()
class Box(BlockContext):
    """
    Box is a a layout element which places children in a box with rounded corners and
    some padding around them.
    Example:
        with gr.Box():
            gr.Textbox(label="First")
            gr.Textbox(label="Last")
    """

    def __init__(
        self,
        *,
        visible: bool = True,
        elem_id: str | None = None,
        **kwargs,
    ):
        """
        Parameters:
            visible: If False, box will be hidden.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
        """
        super().__init__(visible=visible, elem_id=elem_id, **kwargs)

    def get_config(self):
        return {"type": "box", **super().get_config()}

    @staticmethod
    def update(
        visible: bool | None = None,
    ):
        return {
            "visible": visible,
            "__type__": "update",
        }

    def style(self, **kwargs):
        return self


class Form(BlockContext):
    def get_config(self):
        return {"type": "form", **super().get_config()}


@document()
class Accordion(BlockContext):
    """
    Accordion is a layout element which can be toggled to show/hide the contained content.
    Example:
        with gr.Accordion("See Details"):
            gr.Markdown("lorem ipsum")
    """

    def __init__(
        self,
        label,
        *,
        open: bool = True,
        visible: bool = True,
        elem_id: str | None = None,
        **kwargs,
    ):
        """
        Parameters:
            label: name of accordion section.
            open: if True, accordion is open by default.
            elem_id: An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.
        """
        self.label = label
        self.open = open
        super().__init__(visible=visible, elem_id=elem_id, **kwargs)

    def get_config(self):
        return {
            "type": "accordion",
            "open": self.open,
            "label": self.label,
            **super().get_config(),
        }

    @staticmethod
    def update(
        open: bool | None = None,
        label: str | None = None,
        visible: bool | None = None,
    ):
        return {
            "visible": visible,
            "label": label,
            "open": open,
            "__type__": "update",
        }
