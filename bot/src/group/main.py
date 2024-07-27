from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart


from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command

from src.group.module.clear import ClearMessage
from src.group.module.zov import Zov
from src.group.module.staff import Staff
from src.group.module.start import StartBot
from src.group.module.mute import Mute, UnMute, MuteList
from src.group.module.ban import Ban, UnBan, BanList, SearchBan
from src.group.module.warn import Warn, UnWarn, SearchWarn, WarnList
from src.group.module.nickname import NickName, UnNickName, SearchNickName, RemoveNickName
from src.group.module.rank import RankForward


class UserRouter:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.router = Router()
        self.router.message.filter(F.chat.type.in_({"group", "supergroup"}))
        self.register_handlers()

    def register_handlers(self):
        self.router.message.register(self.start_command, Command("start"))

        self.router.message.register(self._mute, Command('mute'))
        self.router.message.register(self._unmute, Command('unmute'))

        self.router.message.register(self._ban, Command('ban'))
        self.router.message.register(self._unban, Command('unban'))

        self.router.message.register(self._warn, Command('warn'))
        self.router.message.register(self._unwarn, Command('unwarn'))

        self.router.message.register(self._snick, Command('snick'))
        self.router.message.register(self._rnick, Command('rnick'))
        self.router.message.register(self._rnickall, Command('rnickall'))

        self.router.message.register(self._gmoder, Command('gmoder'))
        self.router.message.register(self._gadmin, Command('gadmin'))
        self.router.message.register(self._gsenadmin, Command('gsenadmin'))
        self.router.message.register(self._gspec, Command('gspec'))

        self.router.message.register(self._staff, Command('staff'))

        self.router.message.register(self._zov, Command('zov'))

        self.router.message.register(self._gnick, Command('gnick'))

        self.router.message.register(self._gwarn, Command('gwarn'))

        self.router.message.register(self._wlist, Command('wlist'))

        self.router.message.register(self._mlist , Command('mlist'))

        self.router.message.register(self._blist, Command('blist'))

        self.router.message.register(self._clear, Command('clear'))

        self.router.message.register(self._getban, Command('getban'))

        self.router.message.register(self._add_user, F.text)

    async def start_command(self, message: Message):
        await StartBot.start(message, self.bot)

    async def _add_user(self, message: Message):
        await StartBot.add_usere(message, self.bot)

    async def _mute(self, message: Message):
        await Mute.mute(message, self.bot)
    async def _unmute(self, message: Message):
        await UnMute.unmute(message, self.bot)

    async def _ban(self, message: Message):
        await Ban.ban(message, self.bot)
    async def _unban(self, message: Message):
        await UnBan.unban(message, self.bot)

    async def _warn(self, message: Message):
        await Warn.warn(message, self.bot)
    async def _unwarn(self, message: Message):
        await UnWarn.unwarn(message, self.bot)

    async def _snick(self, message: Message):
        await NickName.snick(message, self.bot)
    async def _rnick(self, message: Message):
        await UnNickName.rnick(message, self.bot)
    async def _rnickall(self, message: Message):
        await RemoveNickName.rnickall(message, self.bot)

    async def _gmoder(self, message: Message):
        await RankForward.rank_gmoder(message, self.bot)
    async def _gadmin(self, message: Message):
        await RankForward.rank_gadmin(message, self.bot)
    async def _gsenadmin(self, message: Message):
        await RankForward.rank_gsenadmin(message, self.bot)
    async def _gspec(self, message: Message):
        await RankForward.rank_gspec(message, self.bot)

    async def _staff(self, message: Message):
        await Staff.staff(message, self.bot)

    async def _zov(self, message: Message):
        await Zov.zov(message, self.bot)

    async def _gnick(self, message: Message):
        await SearchNickName.search_gnick(message, self.bot)

    async def _gwarn(self, message: Message):
        await SearchWarn.search_warn(message, self.bot)

    async def _wlist(self, message: Message):
        await WarnList.list_warns(message, self.bot)

    async def _mlist(self, message: Message):
        await MuteList.mute_list(message, self.bot)

    async def _blist(self, message: Message):
        await BanList.ban_list(message, self.bot)

    async def _clear(self, message: Message):
        await ClearMessage.clear(message, self.bot)

    async def _getban(self, message: Message):
        await SearchBan.search_ban(message, self.bot)



