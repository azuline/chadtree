from os import sep
from os.path import abspath
from pathlib import PurePath
from typing import Optional

from pynvim_pp.nvim import Nvim
from std2 import anext

from ..fs.cartographer import is_dir
from ..fs.ops import ancestors, exists, mkdir, new
from ..lsp.notify import lsp_created
from ..registry import rpc
from ..settings.localization import LANG
from ..settings.types import Settings
from ..state.next import forward
from ..state.types import State
from .shared.current import maybe_path_above
from .shared.index import indices
from .shared.refresh import refresh
from .types import Stage


@rpc(blocking=False)
async def _new(state: State, settings: Settings, is_visual: bool) -> Optional[Stage]:
    """
    new file / folder
    """

    node = await anext(indices(state, is_visual=is_visual), None)
    if not node:
        return None
    else:
        parent = node.path.parent
        if is_dir(node) and node.path in state.index:
            parent = node.path

        child = await Nvim.input(question=LANG("pencil"), default="")

        if not child:
            return None
        else:
            path = PurePath(abspath(parent / child))
            if await exists(path, follow=False):
                await Nvim.write(LANG("already_exists", name=str(path)), error=True)
                return None
            else:
                try:
                    if child.endswith(sep):
                        await mkdir((path,))
                    else:
                        await new((path,))
                except Exception as e:
                    await Nvim.write(e, error=True)
                    return await refresh(state=state, settings=settings)
                else:
                    new_state = (
                        await maybe_path_above(state, settings=settings, path=path)
                        or state
                    )
                    paths = ancestors(path)
                    index = state.index | paths
                    next_state = await forward(
                        new_state, settings=settings, index=index, paths=paths
                    )
                    await lsp_created((path,))
                    return Stage(next_state, focus=path)
