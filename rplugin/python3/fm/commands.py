from typing import Optional

from dataclass import asdict
from pynvim import Nvim

from .git import status
from .keymap import keymap
from .nvim import Buffer, Window
from .state import index
from .types import Settings, State
from .wm import is_fm_buffer, update_buffers


def _index(nvim: Nvim, state: State) -> Optional[str]:
    window: Window = nvim.current.window
    row, _ = nvim.api.win_get_cursor(window)
    row = row - 1
    return index(state, row)


def _redraw(nvim: Nvim, state: State) -> None:
    update_buffers(nvim, lines=state.rendered)


async def a_on_filetype(nvim: Nvim, state: State, settings: Settings, buf: int) -> None:
    buffer: Buffer = nvim.buffers[buf]
    keymap(nvim, buffer=buffer, settings=settings)


async def a_on_bufenter(nvim: Nvim, state: State, buf: int) -> State:
    buffer: Buffer = nvim.buffers[buf]
    if is_fm_buffer(nvim, buffer=buffer):
        git = await status()
        return State(**{**asdict(state), **dict(git=git)})
    else:
        return state


async def a_on_focus(nvim: Nvim, state: State) -> State:
    git = await status()
    return State(**{**asdict(state), **dict(git=git)})


async def c_open(nvim: Nvim, state: State) -> State:
    pass


async def c_primary(nvim: Nvim, state: State) -> State:
    pass


async def c_secondary(nvim: Nvim, state: State) -> State:
    pass


async def c_refresh(nvim: Nvim, state: State) -> State:
    pass


async def c_hidden(nvim: Nvim, state: State) -> State:
    pass


async def c_copy_name(nvim: Nvim, state: State) -> None:
    path = _index(nvim, state)
    if path:
        nvim.funcs.setreg("+", path)
        nvim.funcs.setreg("*", path)
        print(nvim, f"📎 {path}")


async def c_new(nvim: Nvim, state: State) -> State:
    pass


async def c_rename(nvim: Nvim, state: State) -> State:
    pass


async def c_select(nvim: Nvim, state: State) -> State:
    pass


async def c_clear(nvim: Nvim, state: State) -> State:
    pass


async def c_delete(nvim: Nvim, state: State) -> State:
    pass


async def c_cut(nvim: Nvim, state: State) -> State:
    pass


async def c_copy(nvim: Nvim, state: State) -> State:
    pass


async def c_paste(nvim: Nvim, state: State) -> State:
    pass
