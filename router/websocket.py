from fastapi import WebSocket, APIRouter, HTTPException, Depends
from fastapi.websockets import WebSocketDisconnect
from router.logout import get_current_user
from router.agoracall import handle_websocket_message

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    if token is None:
        raise HTTPException(status_code=401, detail="Token de autenticación no proporcionado")
    
    # Verifica la autenticación del usuario utilizando la función get_current_user.
    user_email = await get_current_user(token)
    if user_email is None:
        raise HTTPException(status_code=401, detail="Token de autenticación inválido")
    
    # Si la autenticación es exitosa, acepta la conexión WebSocket.
    await websocket.accept()

    try:
        # Aquí puedes implementar la lógica específica de tu aplicación para manejar la comunicación WebSocket.
        while True:
            # Por ejemplo, puedes recibir mensajes del cliente y enviar respuestas.
            data = await websocket.receive_text()
            await handle_websocket_message(websocket, data)
    except WebSocketDisconnect:
        # Maneja la desconexión del cliente si es necesario.
        pass
