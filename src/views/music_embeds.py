import discord

def create_now_playing_embed(info):
    """
    Transforma la información de la canción en un Embed elegante.
    Usa .get() para evitar errores si falta algún dato.
    """
    
    # 1. Extraemos datos con valores por defecto (Seguridad total)
    titulo = info.get('title', 'Canción desconocida')
    url_web = info.get('webpage_url', 'https://www.youtube.com')
    thumb = info.get('thumbnail')
    requester = info.get('requester', 'Sistema')
    duracion_seg = info.get('duration', 0)

    # 2. Configuración del Embed
    embed = discord.Embed(
        title="🎵 Reproduciendo ahora",
        description=f"**[{titulo}]({url_web})**",
        color=discord.Color.from_rgb(43, 45, 49) 
    )

    # 3. Imagen (Thumbnail)
    if thumb:
        embed.set_image(url=thumb)

    # 4. Formateo de Duración
    if duracion_seg and duracion_seg > 0:
        minutos = int(duracion_seg // 60)
        segundos = int(duracion_seg % 60)
        tiempo_fmt = f"{minutos}:{segundos:02d}"
    else:
        tiempo_fmt = "En vivo / Desconocida"

    # 5. Campos de Información
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
    
    # 6. Pie de página
    embed.set_footer(
        text="Sybaru Music • Dale a la ⭐ para guardar en tu playlist",
        icon_url="https://cdn-icons-png.flaticon.com/512/1828/1828884.png"
    )
    
    return embed