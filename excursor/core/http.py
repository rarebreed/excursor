"""
Functions for common HTTP needs
"""


from aiohttp import ClientSession


async def with_session(session: ClientSession):

    async with session.get('http://httpbin.org/get') as resp:
        print(resp.status)
        print(await resp.text())
