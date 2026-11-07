# VideoMCP Architecture

## Flujo 1 — Edición

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

## Flujo 2 — Generación + edición

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

## Responsabilidades

- **MCP:** interfaz de herramientas para el agente.
- **ComfyUI/Wan:** generación opcional de imágenes y clips.
- **Kinocut:** orquestación de edición, timeline, montaje y operaciones de video.
- **FFmpeg:** render y transcodificación final.
- **VideoMCP Studio:** UI web y API local para controlar ambos flujos.

## Principio

Toda salida final debe pasar por Kinocut/FFmpeg. ComfyUI/Wan nunca sustituye la etapa de edición.
