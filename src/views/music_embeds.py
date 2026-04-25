import discord

def create_now_playing_embed(info, loop_active=False):
    """
    Transforma la información de la canción en un Embed elegante.
    Diseño optimizado para Sybaru Music con indicador de estado de Loop.
    """
    
    # 1. Extracción de metadatos con seguridad
    titulo = info.get('title', 'Canción desconocida')
    url_web = info.get('webpage_url', 'https://www.youtube.com')
    thumb = info.get('thumbnail')
    requester = info.get('requester', 'Sistema')
    duracion_seg = info.get('duration', 0)

    # 2. Configuración estética (Color oscuro premium)
    embed = discord.Embed(
        title="🎵 Reproduciendo ahora",
        description=f"**[{titulo}]({url_web})**",
        color=discord.Color.from_rgb(43, 45, 49) 
    )

    # 3. Imagen Principal (Miniatura de YouTube)
    if thumb:
        embed.set_image(url=thumb)

    # 4. Formateo de Duración
    if duracion_seg and duracion_seg > 0:
        minutos = int(duracion_seg // 60)
        segundos = int(duracion_seg % 60)
        tiempo_fmt = f"{minutos}:{segundos:02d}"
    else:
        tiempo_fmt = "En vivo"

    # 5. Campos de Información (Organizados en filas)
    embed.add_field(
        name="⏳ Duración", 
        value=f"`{tiempo_fmt}`", 
        inline=True
    )
    
    embed.add_field(
        name="👤 Pedida por", 
        value=f"`{requester}`", 
        inline=True
    )
    
    # --- CAMPO DINÁMICO DE REPETICIÓN ---
    # Este campo responde directamente al estado en el MusicManager
    status_loop = "✅ Activado" if loop_active else "❌ Desactivado"
    embed.add_field(
        name="🔄 Repetición", 
        value=f"`{status_loop}`", 
        inline=True
    )
    
    # 6. Pie de página 
    embed.set_footer(
        text="Sybaru Music • Dale a la ⭐ para guardar en tu playlist",
        icon_url="https://cdn-icons-png.flaticon.com/512/1828/1828884.png"
    )
    
    return embed