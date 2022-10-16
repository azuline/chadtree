from asyncio import gather
from pathlib import Path

from pynvim_pp.nvim import Nvim

from ..consts import SESSION_DIR
from ..fs.cartographer import new
from ..nvim.markers import markers
from ..settings.types import Settings
from ..version_ctl.types import VCStatus
from ..view.render import render
from .ops import load_session
from .types import Selection, State


async def initial(settings: Settings) -> State:
    cwd, marks = await gather(Nvim.getcwd(), markers())
    session_store = (
        Path(await Nvim.fn.stdpath(str, "cache")) / "chad_sessions"
        if settings.xdg
        else SESSION_DIR
    )

    session = (
        await load_session(cwd, session_store=session_store)
        if settings.session
        else None
    )
    index = session.index if session and session.index is not None else {cwd}

    show_hidden = (
        session.show_hidden
        if session and session.show_hidden is not None
        else settings.show_hidden
    )
    enable_vc = (
        session.enable_vc
        if session and session.enable_vc is not None
        else settings.version_ctl.enable
    )

    selection: Selection = set()
    node = await new(cwd, index=index)
    vc = VCStatus()

    current = None
    filter_pattern = None

    derived = render(
        node,
        settings=settings,
        index=index,
        selection=selection,
        filter_pattern=filter_pattern,
        markers=marks,
        vc=vc,
        show_hidden=show_hidden,
        current=current,
    )

    state = State(
        session_store=session_store,
        index=index,
        selection=selection,
        filter_pattern=filter_pattern,
        show_hidden=show_hidden,
        follow=settings.follow,
        enable_vc=enable_vc,
        width=settings.width,
        root=node,
        markers=marks,
        vc=vc,
        current=current,
        derived=derived,
        window_order={},
    )
    return state
