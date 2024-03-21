import asyncio
import websockets

async def connect_to_paciente_ws():
    async with websockets.connect("ws://localhost:8000/ws/paciente/2") as websocket:
        await websocket.send("Mensaje de prueba para el paciente")
        response = await websocket.recv()
        print("Respuesta del paciente:", response)

asyncio.get_event_loop().run_until_complete(connect_to_paciente_ws())