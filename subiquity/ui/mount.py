
import re

from urwid import connect_signal, Padding, Pile, WidgetWrap

from subiquitycore.ui.interactive import Selector, StringEditor

common_mountpoints = [
    '/',
    '/boot',
    '/home',
    '/srv',
    '/usr',
    '/var',
    '/var/lib',
    ]

class _MountEditor(StringEditor):
    """ Mountpoint input prompt with input rules
    """

    def keypress(self, size, key):
        ''' restrict what chars we allow for mountpoints '''

        mountpoint = r'[a-zA-Z0-9_/\.\-]'
        if re.match(mountpoint, key) is None:
            return False

        return super().keypress(size, key)

class MountSelector(WidgetWrap):
    def __init__(self, model):
        mounts = model.get_mounts2()
        opts = []
        first_opt = None
        max_len = max(map(len, common_mountpoints))
        for i, mnt in enumerate(common_mountpoints):
            devpath = mounts.get(mnt)
            if devpath is None:
                if first_opt is None:
                    first_opt = i
                opts.append((mnt, True, mnt))
            else:
                opts.append(("%-*s (%s)"%(max_len, mnt, devpath), False, None))
        opts.append(('other', True, None))
        self._selector = Selector(opts, first_opt)
        connect_signal(self._selector, 'select', self._select_mount)
        self._other = _MountEditor(edit_text='/')
        super().__init__(Pile([self._selector]))

    def _showhide_other(self, show):
        if show:
            self._w.contents.append((Padding(self._other, left=4), self._w.options('pack')))
        else:
            del self._w.contents[-1]

    def _select_mount(self, sender, value):
        if (self._selector.value == None) != (value == None):
            self._showhide_other(value==None)
        if value == None:
            self._w.focus_position = 1

    @property
    def value(self):
        if self._selector.value is None:
            return self._other.value
        else:
            return self._selector.value
