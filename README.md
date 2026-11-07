# VideoMCP Studio

VideoMCP Studio es un sistema local para Mac que permite crear Reels y videos cortos desde texto, fotos, videos, música y recursos buscados automáticamente.

## Arquitectura

### Edición normal

```
ChatGPT / agente
      ↓
     MCP
      ↓
   Kinocut
      ↓
    FFmpeg
      ↓
   MP4 final
```

### Generación de escenas con IA

```
ChatGPT / agente
      ↓
     MCP
      ↓
 ComfyUI / Wan
      ↓
 clips generados
      ↓
   Kinocut
      ↓
    FFmpeg
      ↓
  Reel final
```

Kinocut es la capa de edición y control de calidad. FFmpeg realiza el render final. ComfyUI/Wan es opcional y se usa únicamente cuando se necesitan escenas generadas.

## Qué puede hacer

- Subir fotos, videos, logos y audio.
- Buscar fotos y videos verticales mediante Pexels.
- Crear Reels 9:16.
- Usar Kinocut para edición y checkpoints de calidad.
- Usar ComfyUI/Wan para generar escenas localmente.
- Exponer herramientas a un agente mediante MCP.
- Guardar los MP4 en el Mac local.
- Ejecutar la interfaz web automáticamente al iniciar sesión.

## Requisitos

- macOS
- Homebrew
- Git
- Python 3.12
- FFmpeg

El instalador principal instala Python, FFmpeg, Kinocut y VideoMCP.

## Instalación en Mac

Abrí Terminal y ejecutá:

```bash
git clone https://github.com/marugaul/marugaul-VideoMCP.git
cd marugaul-VideoMCP
bash scripts/install_mac.sh
```

Al terminar se abre:

```
http://127.0.0.1:8000
```

La web solo escucha en tu Mac.

## ComfyUI / Wan

ComfyUI es opcional:

```bash
bash ~/.videomcp/app/scripts/install_comfyui_mac.sh
```

El instalador no descarga automáticamente los modelos Wan porque pesan varios GB. Los modelos se agregan después según el equipo.

## MCP

Servidor VideoMCP:

```
~/.videomcp/.venv/bin/videomcp-mcp
```

Servidor Kinocut completo:

```
KINOCUT_TOOLS=all ~/.videomcp/.venv/bin/kino --mcp
```

Ejemplo genérico disponible en `mcp.example.json`.

En un cliente MCP local se pueden registrar ambos servidores. Para ChatGPT Desktop, agregá el servidor desde **Settings → MCP servers → Add server**, usando STDIO y el comando local correspondiente, cuando esa opción esté disponible en tu cliente.

## Búsqueda de recursos gratuitos

La integración de Pexels es opcional. Guardá la API key en:

```
~/.videomcp/.env
```

Ejemplo:

```
PEXELS_API_KEY=tu_api_key
```

## Diagnóstico

```bash
~/.videomcp/.venv/bin/videomcp-doctor
~/.videomcp/.venv/bin/kino doctor
```

## Seguridad

VideoMCP escucha únicamente en `127.0.0.1` y no expone la interfaz web públicamente.

No agregues claves API al repositorio. Usá `~/.videomcp/.env`.
