from modules.base_module import Module
import modules.notify as notify
import const

class_name: str = "Billing"
OFF_FREE_GOLD_TEXT: str = "Покупка золотых монет отключена"

class Billing(Module):
    prefix: str = "b"

    def __init__(self, server):
        self.server = server
        self.commands: dict = {"chkprchs": self.check_purchase,
                         "bs": self.buy_silver,
                         "ren": self.buy_energy}
        self.TYPE_PURCHASE: str = "gold"

    async def check_purchase(self, msg, client):
        if self.TYPE_PURCHASE == "gold":
            if await OFF_FREE_GOLD(client):
                return
            amount: int = int(msg[2]["prid"].split("pack")[1])
            if amount < 0:
                return
            user_data: dict = await self.server.get_user_data(client.uid)
            new_gold = user_data["gld"] + amount
            await self.server.redis.set(f"uid:{client.uid}:gld", gold)
            await self.server.redis.set(f"uid:{client.uid}:act",
                                        user_data["act"] + 10)
            await client.send(["acmr.adac", {"vl": 10}])
            await client.send(["b.ingld", {"ingld": amount}])
            await notify.update_resources(client, self.server)

    async def buy_silver(self, msg, client):
        user_data: dict = await self.server.get_user_data(client.uid)
        if user_data['gld'] < msg[2]["gld"]:
            return
        await self.server.redis.set(f"uid:{client.uid}:gld",
                                    user_data['gld'] - msg[2]["gld"])
        await self.server.redis.set(f"uid:{client.uid}:slvr",
                                    user_data['slvr'] + msg[2]["gld"] * 100)
        await client.send(["b.inslv", {"inslv": msg[2]["gld"] * 100}])
        await notify.update_resources(client, self.server)
        
    async def buy_energy(self, msg, client):
        count_energy: int = 100
        user_data: dict = await self.server.get_user_data(client.uid)
        await self.server.redis.set(f"uid:{client.uid}:enrg", count_energy)
        if user_data['gld'] - 3 < 0:
            return
        await client.send(["b.ren", {}])


async def OFF_FREE_GOLD(client) -> bool:
    if not const.FREE_GOLD:
        await client.send(["cp.ms.rsm", {'txt': OFF_FREE_GOLD_TEXT}])
    return not const.FREE_GOLD