import discord
from discord import message 
from discord.ext import commands, tasks
import youtube_dl
from keep_alive import keep_alive

from random import choice

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


client = commands.Bot(command_prefix='.')

status = ['Meu deus, por que fui criado?','Digite .help para os comandos', 'Merda eu existo']

queue = []

loop = False

@client.event
async def on_ready():
    change_status.start()
    print('Build Success!')

@client.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='general')
    await channel.send(f'Bem vindo {member.mention}!  Digite `.help` para detalhes!')

@client.command(name='ping', help='Esse comando mostra tua net de padaria')
async def ping(ctx):
    await ctx.send(A latencia da sua internet é**: {round(client.latency * 1000)}ms')

@client.command(name='oi', help='Esse comando lhe envia uma mensagem de bom dia!')
async def oi(ctx):
    resposta = ['**Deixa eu dormi**', '**tava dormindo e tu veio me acordar T_T**', '**quer o de sempre chefia?**', '**hahahahaha ronaldinho soccer 64**']
    await ctx.send(choice(resposta))

@client.command(name='credito', help='Mostra o grandissimo criador do bot')
async def credito(ctx):
    await ctx.send('**Made by Falchi**')
    await ctx.send('Obrigado ao querido Jian pela ideia')
    await ctx.send('Quem usar Rythm em vez do meu bot vai me deixar triste')

@client.command(name='morra', help='Frases tristes')
async def morra(ctx):
    responses = ['**por qual motivo eu existo?**', '**eu tenho um proposito?**', '**deixa eu quieto**']
    await ctx.send(choice(responses))

@client.command(name='pobre', help='frases amigaveis')
async def pobre(ctx):
    respostinha = ['**Olha o pobretao pedindo comando**', '**Pobre detectado**', '**Baixa renda avistado**']
    await ctx.send(choice(respostinha))

@client.command(name='join', help='Faz o bot conectar em um voicechat')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("Voce nao esta conectado em um chat de voz")
        return    

    else:
        channel = ctx.message.author.voice.channel

    await channel.connect()

@client.command(name='leave', help='Faz o bot sair do canal de voz')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()

@client.command(name='loop', help="Coloca em modo loop")
async def loop_(ctx):
    global loop 

    if loop:
        await ctx.send('Modo loop esta **desligado**')
        loop = False;

    else:
        await ctx.send('Modo loop esta **ligado**')
        loop = True
        

@client.command(name='play', help='Toca som')
async def play(ctx):
    global queue

    server = ctx.message.guild
    voice_channel = server.voice_client

    async with ctx.typing():
        player = await YTDLSource.from_url(queue[0], loop=client.loop)
        voice_channel.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

        if loop: 
            queue.append(queue[0])

        del(queue[0])


    await ctx.send('**Tocando:** {}'.format(player.title))
    

@client.command(name='pause', help='Pausa a musica atual')
async def pause(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client

    voice_channel.pause()

@client.command(name='resume', help='Volta a tocar a musica pausada')
async def resume(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client

    voice_channel.resume()

@client.command(name='stop', help='Para a musica!')
async def stop(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client

    voice_channel.stop()

@client.command(name='queue', help='Bota na fila')
async def queue_(ctx, url):
    global queue 

    queue.append(url)
    await ctx.sen(f'`{url}`adicionada a fila!')

@client.command(name='remove', help='Remove uma url da fila')
async def remove(ctx, number):
    number += 1
    global queue

    try:
        del(queue[int(number)])
        await ctx.send(f'A fila agora `{queue}!`')

    except:
        await ctx.send('Sua fila está **vazia** ou algum outro problema aconteceu!')

@client.command(name='view', help='Visualiza a fila')
async def view(ctx):
    await ctx.send(f'Sua fila é `{queue}!`')    

@tasks.loop(seconds=5)
async def change_status():
    await client.change_presence(activity=discord.Game(choice(status)))


keep_alive()
client.run('Token')
