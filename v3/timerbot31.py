from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext #test
from telegram.error import BadRequest
from telegram import MessageEntity
from telegram import ParseMode, Update, Bot, Message 
from telegram.utils.helpers import escape_markdown
from telegram import InputMediaPhoto, InputMediaVideo
from concurrent.futures import ThreadPoolExecutor
from config import Config, eksekusi, db, cur
from modul import me,bio,afk,qotd,langdetect,setting,berita,rekam,asl,bantuan,media, reputasi, kawalCorona
from modul.kamus import kamus
from tempfile import TemporaryDirectory
from dotenv import load_dotenv
from urllib.parse import urlparse, quote
from check_safety_code import check_code_safety
from logging.handlers import RotatingFileHandler
from pymediainfo import MediaInfo
from pillow_heif import register_heif_opener
from PIL import Image
import random
import traceback
import signal
import subprocess
import logging
import datetime
import re
import time
import sys
import io
import json
import contextlib
import threading
import pprint
import sqlite3
import tarfile
import os
import html
import ast
import requests

load_dotenv()

pathDB = "database"
SUDO = [582005141, 377596941]
RESTART_FILE = '/tmp/bot_restart_info.json'

os.makedirs('logs', exist_ok=True)

def setup_logging():    
    handlers = []
    
    try:
        file_handler = RotatingFileHandler(
            filename='logs/srabat.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8',
            delay=True 
        )
        handlers.append(file_handler)
    except Exception as e:
        print(f"Warning: Could not setup file logging: {e}")

    
    console_handler = logging.StreamHandler()
    handlers.append(console_handler)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    for handler in handlers:
        handler.setFormatter(formatter)
        handler.setLevel(logging.INFO)
        
        if isinstance(handler, logging.FileHandler):
            original_emit = handler.emit
            
            def emit_with_retry(record):
                try:
                    original_emit(record)
                except Exception as e:
                    console_handler.emit(record)
                    error_record = logging.LogRecord(
                        name=record.name,
                        level=logging.ERROR,
                        pathname=record.pathname,
                        lineno=record.lineno,
                        msg=f"Logging error: {str(e)}",
                        args=(),
                        exc_info=None
                    )
                    console_handler.emit(error_record)
            
            handler.emit = emit_with_retry
        
        root_logger.addHandler(handler)

    return root_logger
    
logger = setup_logging()

class bot_timer():
    def __init__(self):
        self.koneksiDatabase()
        self.t1 = threading.Thread(target=self.timer)
        self.t1.start()
        updater = Config.updater
        dp = Config.dp

        dp.add_handler(CommandHandler("log",              self.get_log))
        dp.add_handler(CommandHandler("eval",              self.handle_eval))
        dp.add_handler(CommandHandler("bash",              self.handle_bash))
        dp.add_handler(CommandHandler("restart_pull",              self.restart_pull))
        dp.add_handler(CommandHandler("start",              self.start))
        dp.add_handler(CommandHandler("afk",                afk.set_afk))
        dp.add_handler(CommandHandler("setbio",             bio.set_bio))
        dp.add_handler(CommandHandler("bio",                bio.bio))
        dp.add_handler(CommandHandler("setme",              me.set_me))
        dp.add_handler(CommandHandler("me",                 me.me))
        dp.add_handler(CommandHandler("qotd",               qotd.qotd,      pass_args = True))
        dp.add_handler(CommandHandler("dqotd",              qotd.dqotd,     pass_args = True))
        dp.add_handler(CommandHandler("xqotd",              qotd.xqotd,     pass_args = True))
        dp.add_handler(CommandHandler("rqotd",              qotd.rqotd))
        dp.add_handler(CommandHandler("sqotd",              qotd.sqotd,     pass_args = True))
        dp.add_handler(CommandHandler("setting",            setting.setting,pass_args = True))
        dp.add_handler(CommandHandler("berita",             berita.berita,  pass_args = True))
        dp.add_handler(CommandHandler("baca",               rekam.baca))
        dp.add_handler(CommandHandler("tulis",              rekam.tulis))
        dp.add_handler(CommandHandler("judul",              rekam.judul))
        dp.add_handler(CommandHandler("help",               bantuan.help))
        dp.add_handler(CommandHandler("help_qotd",          bantuan.help_qotd))
        dp.add_handler(CommandHandler("help_timer",         bantuan.help_timer))
        dp.add_handler(CommandHandler("help_jadwal_sholat", bantuan.help_jadwal_sholat))
        dp.add_handler(CommandHandler("agenda",             self.agenda))
        dp.add_handler(CommandHandler("media",              media.media,    pass_args = True))
        dp.add_handler(CommandHandler("smedia",             media.smedia,   pass_args = True))
        dp.add_handler(CommandHandler("xmedia",             media.xmedia))
        dp.add_handler(CommandHandler("rmedia",             media.rmedia))
        dp.add_handler(CommandHandler("cm",                 media.cmedia))
        # dp.add_handler(CommandHandler("umedia",             umedia.echo))
        # dp.add_handler(CommandHandler("usmedia",             umedia.smedia))
        dp.add_handler(CommandHandler("set",                self.set_timer,
                                      pass_args         =   True,
                                      pass_job_queue    =   True,
                                      pass_chat_data    =   True))
        dp.add_handler(CommandHandler("hitung",             self.timer,
                                      pass_chat_data    =   True, 
                                      pass_job_queue    =   True, 
                                      pass_args         =   True))
        dp.add_handler(CommandHandler("rg",                 reputasi.reputasi_good))
        dp.add_handler(CommandHandler("rb",                 reputasi.reputasi_bad))
        # dp.add_handler(CommandHandler("itungin",            kalkulus.itungin))
        dp.add_handler(CommandHandler("cor",        kawalCorona.cor))
        dp.add_handler(CommandHandler("corstat",        kawalCorona.corGraph, pass_args = True))
        dp.add_handler(CommandHandler("lupaUmur",        asl.lupaUmur))
        dp.add_handler(CommandHandler("setUmur",        asl.setUmur, pass_args = True))
        
        dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, asl.asl))
        dp.add_handler(MessageHandler(Filters.entity(MessageEntity.MENTION) | Filters.entity(MessageEntity.TEXT_MENTION) | Filters.reply ,afk.reply_afk),group = 1)
        dp.add_handler(MessageHandler(Filters.all, langdetect.echo),group = 2)
        dp.add_handler(MessageHandler(Filters.text|Filters.video | Filters.photo | Filters.document | Filters.forwarded | Filters.sticker, rekam.isi), group = 3)
        dp.add_handler(MessageHandler(~Filters.command, afk.sudah_nongol), group = 4)
        dp.add_handler(MessageHandler(Filters.text, asl.check_age),group = 5)
        dp.add_handler(MessageHandler(Filters.text, self.cmedia),group = 6)
        self.check_restart_message()
        updater.start_polling()
        updater.idle()

    def check_restart_message(self):
        try:
            if os.path.exists(RESTART_FILE):
                with open(RESTART_FILE, 'r') as f:
                    data = json.load(f)
                    chat_id = data.get('cid')
                    if chat_id:
                        bot = Bot(token = Config.TOKEN)
                        text = f"{data['msg']}\n✅ Bot berhasil direstart!"
                        try:
                            bot.edit_message_text(
                                chat_id=chat_id,
                                message_id=data['message_id'],
                                text=text,
                                parse_mode='Markdown'
                            )
                        except Exception as e:
                            bot.send_message(
                                chat_id=chat_id,
                                text=text,
                                parse_mode='Markdown'
                            )
                os.remove(RESTART_FILE)
        except Exception as e:
            print(f"Error sending restart message: {e}")

    @staticmethod
    def escape_markdown_v2(text):
        special_chars = [
            '_', '*', '[', ']', '(', ')', '~', '`', '>', '#', 
            '+', '-', '=', '|', '{', '}', '.', '!'
        ]
        return ''.join(f'\\{c}' if c in special_chars else c for c in str(text))
    
    def run_command(self, cmd):
        try:
            process = subprocess.run(
                cmd,
                shell=True,
                text=True,
                capture_output=True
            )
            
            success = process.returncode == 0
            output = process.stdout if success else process.stderr
            return success, output.strip()
        except Exception as e:
            return False, str(e)
    
    def handle_bash(self, update, context):
        try:
            user_id = update.message.from_user.id
            if user_id not in SUDO:
                update.message.reply_text(
                    "⚠️ You don't have permission to use this command.",
                    parse_mode='Markdown'
                )
                return
    
            if len(context.args) < 1:
                update.message.reply_text(
                    "**Usage:**\n`/bash command`\n\n"
                    "**Example:**\n`/bash pip install psutil`",
                    parse_mode='Markdown'
                )
                return
    
            cmd = ' '.join(context.args)
    
            if cmd.startswith("pip install"):
                msg = update.message.reply_text(
                    "**Installing module...**",
                    parse_mode='Markdown'
                )
                
                success, output = self.run_command(f"{sys.executable} -m {cmd}")
                
                if success:
                    msg.edit_text(
                        f"**Successfully installed!**\n\n```\n{output}```",
                        parse_mode='Markdown'
                    )
                else:
                    msg.edit_text(
                        f"**Installation failed!**\n\n```\n{output}```",
                        parse_mode='Markdown'
                    )
                return
    
            msg = update.message.reply_text(
                "**Executing...**",
                parse_mode='Markdown'
            )
            
            success, output = self.run_command(cmd)
            temp_output_file = "output_bash.txt"
            if success:
                if len(output) > 4096:
                    with open(temp_output_file, "w+", encoding='utf-8') as file:
                        file.write(output)
                    
                    update.message.reply_document(
                        document=open(temp_output_file, "rb"),
                        caption="**Bash Output**",
                        parse_mode='Markdown'
                    )
                    
                    os.remove(temp_output_file)
                    msg.delete()
                else:
                    msg.edit_text(
                        f"**Output:**\n```\n{output}```",
                        parse_mode='Markdown'
                    )
            else:
                msg.edit_text(
                    f"**Error:**\n```\n{output}```",
                    parse_mode='Markdown'
                )
    
        except Exception as e:
            update.message.reply_text(
                f"**Error executing command:**\n```\n{str(e)}```",
                parse_mode='Markdown'
            )       

    def capture_output(self, code, update):
        stdout_buf = io.StringIO()
        stderr_buf = io.StringIO()
        result = None
        
        if not hasattr(self, 'local_vars'):
            self.local_vars = {
                # Math and Numbers
                'math': __import__('math'),
                'decimal': __import__('decimal'),
                'fractions': __import__('fractions'),
                'random': __import__('random'),
                'statistics': __import__('statistics'),
                
                # Date and Time
                'datetime': __import__('datetime'),
                'time': __import__('time'),
                'calendar': __import__('calendar'),
                
                # Data Processing
                'json': __import__('json'),
                'csv': __import__('csv'),
                're': __import__('re'),  # Regular expressions
                
                # String Operations
                'string': __import__('string'),
                
                # Data Structures
                'collections': __import__('collections'),
                'array': __import__('array'),
                'itertools': __import__('itertools'),
                
                # System Info (Read-only)
                'sys': __import__('sys'),
                'platform': __import__('platform'),
                
                # Utility
                'typing': __import__('typing'),
                'enum': __import__('enum'),
                'uuid': __import__('uuid'),
                
                # Previous result store
                '_': None,
                
                # Module info
                '__name__': '__main__',
                '__package__': None,
                
                # Useful constants
                'True': True,
                'False': False,
                'None': None,
                
                # Helper functions
                'len': len,
                'range': range,
                'round': round,
                'sum': sum,
                'min': min,
                'max': max,
                'abs': abs,
                'all': all,
                'any': any,
                'enumerate': enumerate,
                'zip': zip,
                'map': map,
                'filter': filter,
                'sorted': sorted,
                'reversed': reversed,
                'randint': random.randint,
                'choice': random.choice,
                'shuffle': random.shuffle,
                'timestamp': lambda: datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'pretty': lambda x: json.dumps(x, indent=2, ensure_ascii=False),
                'to_date': lambda x: datetime.datetime.strptime(x, '%Y-%m-%d'),
                'to_datetime': lambda x: datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S'),
                'self': self
            }
            
        self.local_vars.update({
            'update': update,
            'msg': update.effective_message, 
            'rm': update.effective_message.reply_to_message,
            'chat': update.effective_chat,
            'user': update.effective_user,
        })

        # referensi: https://github.com/penn5/meval/blob/master/meval/__init__.py
        def _meval(code, globs):
            locs = {}
            globs = globs.copy()
    
            try:
                root = ast.parse(code, "exec")
                code_ast = root.body
    
                ret_name = "_ret"
                while ret_name in globs or any(isinstance(node, ast.Name) and node.id == ret_name 
                                             for node in ast.walk(root)):
                    ret_name = "_" + ret_name
    
                if not code_ast:
                    return None
    
                if not any(isinstance(node, ast.Return) for node in code_ast):
                    for i in range(len(code_ast)):
                        if isinstance(code_ast[i], ast.Expr):
                            if i == len(code_ast) - 1 or not isinstance(code_ast[i].value, ast.Call):
                                code_ast[i] = ast.copy_location(
                                    ast.Expr(ast.Call(
                                        func=ast.Attribute(
                                            value=ast.Name(id=ret_name, ctx=ast.Load()),
                                            attr="append",
                                            ctx=ast.Load()
                                        ),
                                        args=[code_ast[i].value],
                                        keywords=[]
                                    )),
                                    code_ast[-1]
                                )
    
                ret_decl = ast.Assign(
                    targets=[ast.Name(id=ret_name, ctx=ast.Store())],
                    value=ast.List(elts=[], ctx=ast.Load())
                )
                ast.fix_missing_locations(ret_decl)
                code_ast.insert(0, ret_decl)
                code_ast.append(
                    ast.Return(value=ast.Name(id=ret_name, ctx=ast.Load()))
                )
    
                fun = ast.FunctionDef(
                    name="tmp",
                    args=ast.arguments(
                        args=[],
                        posonlyargs=[],
                        kwonlyargs=[],
                        kw_defaults=[],
                        defaults=[],
                        vararg=None,
                        kwarg=None
                    ),
                    body=code_ast,
                    decorator_list=[],
                    returns=None
                )
                ast.fix_missing_locations(fun)
                mod = ast.parse("")
                mod.body = [fun]
    
                comp = compile(mod, "<string>", "exec")
                exec(comp, globs, locs)
    
                r = locs["tmp"]()
    
                if isinstance(r, list):
                    r = [x for x in r if x is not None]
                    return r[0] if len(r) == 1 else r if r else None
                return r
    
            except Exception:
                traceback.print_exc(file=stderr_buf)
                return None
    
        with contextlib.redirect_stdout(stdout_buf), contextlib.redirect_stderr(stderr_buf):
            try:
                result = _meval(code, self.local_vars)
                
                if result is not None:
                    self.local_vars['_'] = result
                    if isinstance(result, (Message, Update)):
                        result = json.dumps(result.to_dict(), indent=2, default=str)
                    elif isinstance(result, (dict, list, tuple, set)):
                        result = json.dumps(result, indent=2, default=str)
                    elif hasattr(result, '__dict__') and not isinstance(result, type):
                        result = json.dumps(result.__dict__, indent=2, default=str)
                    
            except Exception:
                traceback.print_exc(file=stderr_buf)
                result = None
    
        stdout = stdout_buf.getvalue()
        stderr = stderr_buf.getvalue()
        
        stdout_buf.close()
        stderr_buf.close()
        
        result_str = str(result) if result is not None else ""
        if stdout and not result:
            result_str = ""
            
        return stdout, stderr, result_str
    
    def handle_eval(self, update, context):
        try:
            user_id = update.message.from_user.id
            if user_id not in SUDO:
                update.message.reply_text(
                    "⚠️ You don't have permission to use this command.",
                    parse_mode='Markdown'
                )
                return
    
            if len(context.args) < 1:
                update.message.reply_text(
                    "**Usage:**\n`/eval python_code`\n\n"
                    "**Example:**\n`/eval 2 + 2`\n"
                    "`/eval import platform; platform.python_version()`",
                    parse_mode='Markdown'
                )
                return
    
            code = update.message.text.split(None, 1)[1]
            
            dangerous_patterns = [
                'subprocess', 'eval(', 'exec(',
                'file.', '.unlink(',
                'shutil', 'rmtree'
            ]
            if any(pattern in code.lower() for pattern in dangerous_patterns):
                update.message.reply_text(
                    "⚠️ Operation not permitted for security reasons.",
                    parse_mode='Markdown'
                )
                return
    
            msg = update.message.reply_text(
                "**Evaluating...**",
                parse_mode='Markdown'
            )
    
            stdout, stderr, result = self.capture_output(code, update)
    
            output_parts = []
            if stdout:
                output_parts.append(f"**Stdout:**\n```\n{stdout}```")
            if stderr:
                output_parts.append(f"**Stderr:**\n```\n{stderr}```")
            if result:
                output_parts.append(f"**Result:**\n```\n{result}```")
    
            output_text = "\n\n".join(output_parts) if output_parts else "*(No output)*"
    
            if len(output_text) > 4096:
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                temp_output_file = f'output_eval_{timestamp}.txt'
                
                try:
                    with open(temp_output_file, "w+", encoding='utf-8') as file:
                        file.write(f"Code:\n{code}\n\n{output_text}")
                    
                    with open(temp_output_file, "rb") as file:
                        update.message.reply_document(
                            document=file,
                            caption=escape_markdown(f"Eval Output - {timestamp}"),
                            parse_mode='Markdown'
                        )
                finally:
                    if os.path.exists(temp_output_file):
                        os.remove(temp_output_file)
                
                msg.delete()
            else:
                full_message = f"**Code:**\n```python\n{code}```\n\n{output_text}"
                try:
                    msg.edit_text(full_message, parse_mode='Markdown')
                except BadRequest:
                    msg.edit_text(escape_markdown(full_message), parse_mode='Markdown')
    
        except Exception as e:
            error_traceback = traceback.format_exc()
            error_message = f"**Error executing code:**\n\n{error_traceback}"
            
            if len(error_message) > 4096:
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                temp_error_file = f'error_eval_{timestamp}.txt'
                
                try:
                    with open(temp_error_file, "w+", encoding='utf-8') as file:
                        file.write(f"Code:\n{code}\n\n{error_message}")
                    
                    with open(temp_error_file, "rb") as file:
                        update.message.reply_document(
                            document=file,
                            caption=escape_markdown(f"Eval Error Log - {timestamp}"),
                            parse_mode='Markdown'
                        )
                finally:
                    if os.path.exists(temp_error_file):
                        os.remove(temp_error_file)
            else:
                try:
                    update.message.reply_text(error_message, parse_mode='Markdown')
                except BadRequest:
                    update.message.reply_text(escape_markdown(error_message), parse_mode='Markdown')
    
    def cmedia(self, update, context):
        if not update.effective_message: return
        message = update.effective_message.text
        
        args = re.search(r'(https?://[^\s]+)', message)
        if args == None:
            return
        args = args.group()
        hostname = urlparse(args).hostname
        
        if hostname == 'twitter.com' or hostname == 'x.com':
            sosmed = "api/twit"
        elif ('facebook' in hostname) or ('fb' in hostname):
            sosmed = "api/fb"
        elif 'threads' in hostname:
            sosmed = "api/thread"
        elif 'instagram' in hostname:
            sosmed = "api/ig"
        elif hostname in ('tiktok.com', 'vt.tiktok.com', 'vm.tiktok.com'):
            sosmed = "api/tiktok"
        else:                
            return
        
        arsip = os.environ.get('API_SOCMED', None)
    
        if not arsip:
            logger.error(f"[{datetime.datetime.now()}] API_SOCMED environment variable not set")
            return update.message.reply_text('api socmed tidak terdeteksi, ketik `export API_SOCMED=url`, di terminal anda untuk export api nya', parse_mode='Markdown')

        bot = context.bot    
        chat_id = update.message["chat"]["id"]
    
        endpoint = f"?url={args}"
        link = f"{arsip}{sosmed}{endpoint}"
                
        def _caption(caption):
            if caption and len(caption) + len(args) >= 1024:
                read_more = '...'
                caption = caption[:1024 - len(read_more)] + read_more if len(caption) > 1024 else caption
            if caption:
                caption = escape_markdown(caption)
            return caption
            
        try:
            req = requests.get(link).json()
        except Exception as e:
            logger.error(f"[{datetime.datetime.now()}] API request failed: {str(e)}")
            return update.message.reply_text(f"Failed to fetch media")
    
        if req.get('success'):
            medias = []
    
            if sosmed == "api/tiktok" and req.get('video'):
                medias.append(InputMediaVideo(req['video'][-1], caption=_caption(req.get('caption')), thumb=req.get('thumbnail'), parse_mode='Markdown'))
            else:
                media_results = req.get('media') or req.get('photos')
                total_media_res = len(media_results) if media_results else 0
                
                if media_results:
                    for i, m in enumerate(media_results):
                        caption = _caption(caption = f"{args}\n{req.get('caption', '')}") if i == total_media_res - 1 else None
                        try:
                            if sosmed == "api/tiktok":
                                medias.append(InputMediaPhoto(m, caption=caption, parse_mode='Markdown'))
                            elif m['type'].upper() != 'VIDEO':
                                if sosmed == 'api/thread':
                                    medias.append(InputMediaPhoto(m['media_url'], caption=caption, parse_mode='Markdown'))
                                elif sosmed == "api/fb":
                                    medias.append(InputMediaPhoto(m['imageHigh'], caption=caption, parse_mode='Markdown'))
                                else:
                                    medias.append(InputMediaPhoto(m['url'], caption=caption, parse_mode='Markdown'))
                            else:
                                thumb = m.get('thumbnail')
                                if sosmed == 'api/thread':
                                    medias.append(InputMediaVideo(m['media_url'], caption=caption, thumb=thumb, parse_mode='Markdown'))
                                elif sosmed == "api/fb":
                                    medias.append(InputMediaVideo(m.get('hd_url') or m.get('sd_url'), caption=caption, thumb=thumb, parse_mode='Markdown'))
                                else:
                                    medias.append(InputMediaVideo(m['url'], caption=caption, thumb=thumb, parse_mode='Markdown'))
                        except Exception as e:
                            logger.error(f"[{datetime.datetime.now()}] Error processing media item {i+1}: {str(e)}")
    
            if len(medias) == 0:
                caption = req.get('caption') or req.get('text')
                if not caption:
                    return
                update.message.reply_text(caption)
            else:                    
                try:
                    self.send_media_chunk(bot, chat_id, medias)
                except BadRequest:
                    self.reply_downloaded_media_chunk(bot, chat_id, medias)
                except Exception as e:
                    logger.error(f"[{datetime.datetime.now()}] Failed to send media: {str(e)}")
                    return update.message.reply_text("Failed to send media")
                if sosmed == 'api/tiktok' and not req.get('video'):
                    with TemporaryDirectory() as tdir:
                        merg_name = f"{tdir}/output_{update.message.message_id}.mp4"
                        audio_path = self.downloader_media(tdir, req['music'][0])['file']
                        self.create_slideshow_ffmpeg(tdir, medias, audio_path, merg_name)
                        # slide = self.create_slideshow_ffmpeg_in_background(tdir, medias, audio_path, merg_name)
                        # slide.join()
                        with open(merg_name, "rb") as slide_photo:
                            update.message.reply_video(slide_photo)
                if len(message.split()) < 2:
                    update.message.delete()
        else:
            error_msg = req.get('msg') or "gagal"
            logger.error(f"[{datetime.datetime.now()}] API request failed with message: {error_msg}")
            update.message.reply_text(error_msg)

    @staticmethod
    def send_media_chunk(bot, chat_id, successful_medias):
        CHUNK_SIZE = 10
        for i in range(0, len(successful_medias), CHUNK_SIZE):
            chunk = successful_medias[i:i + CHUNK_SIZE]
            bot.send_media_group(chat_id=chat_id, media=chunk)

    def create_slideshow_ffmpeg(
        self,
        dir,
        image_paths,
        audio_path,
        output_path,
        duration_per_image=3,
        threads=32
    ):
        concat_file = f"{dir}/images.txt"
        slideshow_video = f"{dir}/slideshow_temp.mp4"
        temp_audio = f"{dir}/audio_temp.aac"

        with ThreadPoolExecutor(max_workers=5) as executor:
            image_paths = list(executor.map(lambda m: self.downloader_media(dir, m.media), image_paths))
        print(image_paths)
        cmd_probe_audio = [
            "ffprobe", 
            "-hide_banner", "-loglevel", "error",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            audio_path
        ]
        result = subprocess.run(cmd_probe_audio, capture_output=True, text=True, check=True)
        audio_duration = float(result.stdout.strip())
        
        if len(image_paths) == 1:
            single_image = os.path.abspath(image_paths[0]['file'])
            cmd_single = [
                "ffmpeg", "-y",
                "-hide_banner", "-loglevel", "error",
                "-threads", str(threads),
                "-loop", "1", 
                "-i", single_image,
                "-t", str(audio_duration),
                "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
                "-pix_fmt", "yuv420p",
                "-c:v", "libx264",
                slideshow_video
            ]
            subprocess.run(cmd_single, check=True)
    
            cmd_copy_audio = [
                "ffmpeg", "-y",
                "-hide_banner", "-loglevel", "error",
                "-threads", str(threads),
                "-i", audio_path,
                "-c:a", "aac",
                temp_audio
            ]
            subprocess.run(cmd_copy_audio, check=True)
    
        else:
            with open(concat_file, "w") as f:
                for i, img in enumerate(image_paths):
                    f.write(f"file '{os.path.abspath(img['file'])}'\n")
                    if i < len(image_paths) - 1:
                        f.write(f"duration {duration_per_image}\n")
    
            cmd_slideshow = [
                "ffmpeg", "-y",
                "-hide_banner",        
                "-loglevel", "error",  
                "-threads", str(threads),
                "-f", "concat", "-safe", "0",
                "-i", concat_file,
                "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
                "-pix_fmt", "yuv420p",
                "-c:v", "libx264",
                slideshow_video
            ]
            subprocess.run(cmd_slideshow, check=True)
    
            cmd_probe_slideshow = [
                "ffprobe", 
                "-hide_banner", "-loglevel", "error",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                slideshow_video
            ]
            result = subprocess.run(cmd_probe_slideshow, capture_output=True, text=True, check=True)
            slideshow_duration = float(result.stdout.strip())
    
            if audio_duration < slideshow_duration:
                cmd_loop_audio = [
                    "ffmpeg", "-y",
                    "-hide_banner", "-loglevel", "error",
                    "-threads", str(threads),
                    "-stream_loop", "-1",
                    "-i", audio_path,
                    "-t", str(slideshow_duration),
                    "-c:a", "aac",
                    temp_audio
                ]
                subprocess.run(cmd_loop_audio, check=True)
            else:
                cmd_trim_audio = [
                    "ffmpeg", "-y",
                    "-hide_banner", "-loglevel", "error",
                    "-threads", str(threads),
                    "-i", audio_path,
                    "-t", str(slideshow_duration),
                    "-c:a", "aac",
                    temp_audio
                ]
                subprocess.run(cmd_trim_audio, check=True)
    
            os.remove(concat_file)
    
        cmd_combine = [
            "ffmpeg", "-y",
            "-hide_banner", "-loglevel", "error",
            "-threads", str(threads),
            "-i", slideshow_video,
            "-i", temp_audio,
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            output_path
        ]
        subprocess.run(cmd_combine, check=True)

    def create_slideshow_ffmpeg_in_background(
        self,
        dir,
        image_paths,
        audio_path,
        output_path,
        duration_per_image=3,
        threads=32
    ):
        t = threading.Thread(
            target=self.create_slideshow_ffmpeg,
            args=(dir, image_paths, audio_path, output_path, duration_per_image, threads),
            daemon=True
        )
        t.start()
        return t
    
    def downloader_media(self, temp_dir, media_url, ext=None):
        try:
            response = requests.get(media_url, stream=True)
            response.raise_for_status()            
            content_type = response.headers.get('content-type', '')
            extension = '.' + (content_type.split('/')[-1] if '/' in content_type else 'tmp')
            
            filename = f"media_{os.urandom(4).hex()}{ext or extension}"
            filepath = os.path.join(temp_dir, filename)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        
            if '.heic' in media_url:
                filepath = self.convert_heic_to_jpeg(filepath) or filepath
                
            return {
                'file': filepath,
                'success': True,
                'size': os.path.getsize(filepath)
            }
        
        except Exception as e:
            return {
                'file': None,
                'success': False,
                'error': str(e)
            }

    @staticmethod
    def convert_heic_to_jpeg(input_path, max_size=320, quality=75):
        try:
            register_heif_opener()
            image = Image.open(input_path)
            image = image.convert('RGB')
            
            width, height = image.size
            ratio = min(max_size/width, max_size/height)
            new_size = (int(width * ratio), int(height * ratio))
            
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            new_path = input_path.rsplit('.', 1)[0] + '.jpg'
            
            current_quality = quality
            while current_quality > 5: 
                image.save(new_path, 'JPEG', quality=current_quality, optimize=True)
                if os.path.getsize(new_path) <= 200 * 1024:
                    break
                current_quality -= 5
                
            return new_path
        except Exception as e:
            print(f"HEIC Conversion error: {str(e)}")
            return None
            
    def reply_downloaded_media_chunk(self, bot, chat_id, medias):
        with TemporaryDirectory() as tdir:
            with ThreadPoolExecutor(max_workers=5) as executor:
                media_results = list(executor.map(lambda m: self.downloader_media(tdir, m.media), medias))
                thumbnail_results = list(executor.map(lambda m: self.downloader_media(tdir, m.thumb) if getattr(m, 'thumb', None) else {'success': False}, medias))
    
                successful_medias = []
                opened_files = []
                for media, media_result, thumb_result in zip(medias, media_results, thumbnail_results):
                    if media_result['success']:
                        f = open(media_result['file'], 'rb')
                        opened_files.append(f)
                        caption = getattr(media, 'caption', None)
                        
                        if media.type == 'photo':
                            media_obj = InputMediaPhoto(
                                f, 
                                caption=caption, 
                                parse_mode='Markdown'
                            )
                        elif media.type == 'video':
                            thumbnail = {}
                            # if '.heic' in media.thumb:
                            #     bot.send_message(Config.BOT_CHAT_ID, thumb_result)
                            if thumb_result.get('success'):
                                thumbnail['thumb'] = open(thumb_result['file'], 'rb')
                                opened_files.append(thumbnail['thumb'])
                                # if '.heic' in media.thumb:
                                #     bot.send_message(Config.BOT_CHAT_ID, thumb_result['file'])
                                #     bot.send_photo(Config.BOT_CHAT_ID, thumbnail['thumb'])
                            duration = round(MediaInfo.parse(media_result['file']).tracks[0].duration / 1000)
                            
                            media_obj = InputMediaVideo(
                                f, 
                                caption=caption, 
                                parse_mode='Markdown',
                                duration=duration,
                                **thumbnail
                            )
                        successful_medias.append(media_obj)

            try:
                self.send_media_chunk(bot, chat_id, successful_medias)
            except Exception as e:
                logger.error(f"[{datetime.datetime.now()}] Failed to send media: {str(e)}")
                bot.send_message(chat_id, "Failed to send media")
            finally:
                for file in opened_files:
                    file.close()
    
    def get_log(self, update, context):
        user_id = update.message.from_user.id
        if user_id not in SUDO:
            return update.message.reply_text("⚠️ You don't have permission to access logs.")
    
        if not context.args:
            return update.message.reply_text(
                "**Usage:**\n"
                "`/log`         - Send all logs\n"
                "`/log -cut N`  - Send last N lines\n"
                "`/log -trun`   - Truncate log file\n"
                "`/log -trun filename` - Truncate specific log",
                parse_mode='Markdown'
            )
    
        if '-trun' in context.args:
            try:
                if len(context.args) < 2 or context.args[0] == '-trun':
                    file_path = "srabat.log"  
                else:
                    file_path = f"{context.args[1]}.log"
    
                full_path = os.path.join('logs', file_path)
    
    
                if not os.path.abspath(full_path).startswith(os.path.abspath('logs')):
                    return update.message.reply_text("⚠️ Invalid file path")
    
                with open(full_path, 'w') as file:
                    file.truncate(0)
                return update.message.reply_text(f"File '{file_path}' has been truncated successfully.")
                
            except Exception as e:
                return update.message.reply_text(
                    f"Failed to truncate file '{file_path}': {str(e)}"
                )
    
        wait_msg = update.message.reply_text('wait...')
        directory_path = 'logs'
        
        try:
            files = os.listdir(directory_path)
        except FileNotFoundError:
            wait_msg.delete()
            return update.message.reply_text("Logs directory not found")
        except Exception as e:
            wait_msg.delete()
            return update.message.reply_text(f"Error accessing logs directory: {str(e)}")
    
        for file in files:
            file_path = os.path.join(directory_path, file)
            if os.path.isfile(file_path):
                try:
                    if '-cut' in update.message.text:
                        match = re.search(r'\d+', update.message.text)
                        num = int(match.group()) if match else 100
                        
                        with open(file_path, 'r') as f:
                            lines = f.readlines()
                            last_lines = ''.join(lines[-num:])
                            
                        if len(last_lines) > 4096:
                            bio = io.BytesIO(last_lines.encode())
                            bio.name = f"{file}_last_{num}_lines.txt"
                            update.message.reply_document(
                                document=bio,
                                filename=bio.name,
                                caption=f"Last {num} lines of {file}"
                            )
                        else:
                            update.message.reply_text(last_lines, parse_mode=None)
                    else:
                        with open(file_path, 'rb') as f:
                            update.message.reply_document(
                                document=f,
                                filename=file,
                                caption=f"Full log file: {file}"
                            )
                            
                except Exception as e:
                    update.message.reply_text(
                        f"Failed to send log file '{file}': {str(e)}"
                    )
        
        try:
            wait_msg.delete()
        except:
            pass
    
    def start(self,update,context):
        try:
            z = self.t1.is_alive()
        except:            
            self.t1 = threading.Thread(target=self.timer)
            self.t1.start()        
        update.message.reply_text(kamus("cmd_start"))

    def set_tanggal(self,update,context,args):
        try:
            current = datetime.datetime.now()+datetime.timedelta(seconds = 0, hours=0)
            self.hitung(update,context,args,int((datetime.datetime.strptime("%s %s"%(args[0], args[1]),"%Y-%m-%d %H:%M:%S")-current).total_seconds())+1)
        except:
            update.message.reply_text(kamus("cmd_error"))

    def set_jam(self,update,context, args):
        now = '{:%Y-%m-%d}'.format(datetime.datetime.now()+datetime.timedelta(seconds = 0, hours=0))
        try:
            current = datetime.datetime.now()+datetime.timedelta(seconds = 0, hours=0)
            self.hitung(update,context,int((datetime.datetime.strptime(now+" "+args[0],"%Y-%m-%d %H:%M:%S")-current).total_seconds())+1)
        except:
            self.set_tanggal(update,context, args)

    def jadwal_sholat(self,update,context, kota):
        try:
            z           = self.t1.is_alive()
            nama        = kota            
            sekarang    = datetime.datetime.now()
            tanggal     = sekarang.strftime('%Y-%m-%d')
            jam         = sekarang.strftime('%H:%M')
            hari        = datetime.datetime.strftime(sekarang.date(),"%a")
            chat_id     = update.message["chat"]["id"]
            chat_type   = update.message["chat"]["type"]
            user_id     = update.message.from_user.id
            user_name   = update.message.from_user.username
            cek         = "SELECT waktu FROM daftar_timer WHERE kota = '%s' AND DATE(waktu) = '%s' AND chat_id = '%s'"%(nama,tanggal,chat_id)
            bar, jum    = eksekusi(cek)
            if jum == 0:                
                url_kota= "https://api.banghasan.com/sholat/format/json/kota"
                r       = requests.get(url_kota)
                kota_all= r.json()['kota']
                mirip   = []
                for a in kota_all:
                    if a['nama'] == nama.upper() or a['id'] == nama:
                        if a['id'] == nama: nama = a['nama']
                        update.message.reply_text(str(kamus("id_ketemu"))%a['id'])
                        url         = "https://api.banghasan.com/sholat/format/json/jadwal/kota/%s/tanggal/%s"%(a['id'],tanggal)            
                        r           = requests.get(url)
                        sholat_all  =  r.json()['jadwal']['data']
                        jadwal      = []
                        t           = ""
                        m           = ""
                        for k,v in sholat_all.items():
                            if k != 'tanggal':
                                waktu = '%s %s:00'%(tanggal,v)
                                if k == 'terbit' or k == 'imsak':
                                    keterangan = "waktu"
                                else:
                                    keterangan = "sholat"

                                if k == 'terbit':t = datetime.datetime.strptime(v,'%H:%M')
                                if k == 'maghrib':m = datetime.datetime.strptime(v,"%H:%M")
                                if hari == "Fri" and k == "dzuhur":                                    
                                    sholat = "jumat"
                                else:
                                    sholat = k                                
                                if jam < v:                                    
                                    status = ""
                                    sql = "INSERT INTO daftar_timer (waktu, chat_id, chat_type, user_id, user_name, pesan, done, sholat, kota) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(
                                            waktu, chat_id, chat_type, user_id, user_name, keterangan, 0,sholat,nama)                            
                                    cur.execute(sql)
                                    db.commit()
                                else:
                                    status = (kamus("sholat_lewat"))
                                jadwal.append('%s %s %s'%(v,sholat,status))
                        tahajud = (t-((m-t)/3)).strftime("%H:%M")
                        if jam < tahajud:
                            status = ""
                            waktu_tahajud = '%s %s:00'%(tanggal,tahajud)
                            sql = "INSERT INTO daftar_timer (waktu, chat_id, chat_type, user_id, user_name, pesan, done, sholat, kota) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(
                                   waktu_tahajud, chat_id, chat_type, user_id, user_name, "sholat", 0,"tahajud",nama)                            
                            cur.execute(sql)
                            db.commit()
                        else:
                            status = (kamus("sholat_lewat"))
                        jadwal.append('%s %s %s'%(tahajud,'tahajud',status))
                        jadwal.sort()
                        agenda_sholat =''.join('%s \n'%jadwal[i] for i in range(len(jadwal)))
                        update.message.reply_text(str(kamus("sholat_jadwal"))%(nama,tanggal,agenda_sholat))
                        break
                    elif re.search(f"{nama}", a['nama'], re.IGNORECASE):
                        mirip.append(f"`{escape_markdown(a['nama'])}`")
                else:
                    # update.message.reply_text(kamus("kota_tidak_ketemu")%url_kota)
                    pesan = kamus("kota_ketemu_sebagian")%"\n- ".join(mirip) if len(mirip)>0 else kamus("kota_tidak_ketemu")%url_kota
                    update.message.reply_text(pesan,parse_mode=ParseMode.MARKDOWN)
            else:
                update.message.reply_text(str(kamus("sholat_sudah_setting")%nama))
        except Exception as e:     
                   
            update.message.reply_text('%s\n%s'%(kamus("mogok"),e))

    def restart_pull(self, update, context):
        user_id = update.message.from_user.id
        if user_id not in SUDO:
            update.message.reply_text("❌ Anda tidak memiliki akses untuk menggunakan perintah ini.")
            return
    
        try:
            message = update.message.reply_text("🔄 Memeriksa pembaruan dari GitHub...")
            
            try:
                subprocess.check_output(['git', 'fetch'], stderr=subprocess.STDOUT, text=True)
            except subprocess.CalledProcessError as e:
                message.edit_text(f"❌ Gagal fetch dari remote:\n```\n{e.output}```", parse_mode='Markdown')
                return
    
            # try:
            #     current_branch = subprocess.check_output(
            #         ['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
            #         stderr=subprocess.STDOUT, 
            #         text=True
            #     ).strip()
            # except subprocess.CalledProcessError as e:
            #     message.edit_text(f"❌ Gagal mendapatkan current branch:\n```\n{e.output}```", parse_mode='Markdown')
            #     return
            current_branch = 'master'
    
            try:
                ignore_patterns = [
                    'config.py'
                ]
        
                # Create exclude pathspec
                exclude_pattern = ' '.join([f':!{pattern}' for pattern in ignore_patterns])
                
                # Get diff with exclusions
                diff_command = ['git', 'diff', '--name-only', f'HEAD..origin/{current_branch}', '--'] + [exclude_pattern]

                diff_output = subprocess.check_output(
                    diff_command, 
                    stderr=subprocess.STDOUT, 
                    text=True
                ).strip()
                
                if not diff_output:
                    message.edit_text("✅ Tidak ada pembaruan yang tersedia.")
                    return
                    
                changed_files = diff_output.split('\n')
                message.edit_text("🔍 Memeriksa file yang diperbarui...")
                
                for file in changed_files:
                    if file.endswith('.py'):
                        try:
                            remote_content = subprocess.check_output(
                                ['git', 'show', f'origin/{current_branch}:{file}'], 
                                stderr=subprocess.STDOUT, 
                                text=True
                            )
                            
                            is_safe, error_msg = check_code_safety(remote_content, file)
                            if not is_safe:
                                try:
                                    message.edit_text(f"❌ Error terdeteksi di `{file}`:\n{error_msg}", parse_mode='Markdown')
                                except BadRequest:
                                    message.edit_text(f"❌ Error terdeteksi di `{file}`:\n{escape_markdown(error_msg)}", parse_mode='Markdown')
                                return
                                
                        except subprocess.CalledProcessError as e:                            
                            try:
                                error_text = (
                                    f"❌ Error saat memeriksa file `{file}`:\n"
                                    f"```\n{e.output}```"
                                )
                                message.edit_text(error_text, parse_mode='Markdown')
                            except BadRequest:
                                error_text = (
                                    f"❌ Error saat memeriksa file `{file}`:\n"
                                    f"```\n{escape_markdown(e.output)}```"
                                )
                                message.edit_text(error_text, parse_mode='Markdown')
                            return
                            
                message.edit_text("✅ Pemeriksaan sintaks berhasil.\n🔄 Mengambil pembaruan...")
                
            except subprocess.CalledProcessError as e:
                message.edit_text(f"❌ Gagal memeriksa perubahan:\n```\n{e.output}```", parse_mode='Markdown')
                return
    
            status_result = subprocess.run(['git', 'status', '--porcelain'], 
                                         capture_output=True, 
                                         text=True)
            
            if status_result.stdout.strip():
                message.edit_text("📝 Ditemukan perubahan lokal, mencoba auto-stash...")
                
                stash_result = subprocess.run(
                    ['git', 'stash', 'save', f"Auto stash before pull at {datetime.datetime.now()}"], 
                    capture_output=True, 
                    text=True
                )
                
                if stash_result.returncode != 0:
                    message.edit_text(
                        f"❌ Gagal melakukan auto-stash:\n```\n{stash_result.stderr}```", 
                        parse_mode='Markdown'
                    )
                    return
                
                message.edit_text("✅ Berhasil menyimpan perubahan lokal dengan stash")
    
            pull_result = subprocess.run(['git', 'pull', 'origin', current_branch], 
                                       capture_output=True, 
                                       text=True)
            
            if pull_result.returncode != 0:
                message.edit_text(
                    f"❌ Gagal melakukan git pull:\n```\n{pull_result.stderr}```", 
                    parse_mode='Markdown'
                )
                return
    
            if status_result.stdout.strip():
                stash_pop = subprocess.run(['git', 'stash', 'pop'], 
                                         capture_output=True, 
                                         text=True)
                if stash_pop.returncode != 0:
                    message.edit_text("⚠️ Berhasil pull tapi gagal mengembalikan perubahan lokal. Silakan cek git stash list.")
                    return
                    
            prev_msg = f"✅ Pembaruan berhasil!\nBranch: `{current_branch}`\n📝 Git pull output:\n```\n{escape_markdown(pull_result.stdout)}\n```"
            
            with open(RESTART_FILE, 'w') as f:
                json.dump({'cid': message.chat.id, 'message_id': message.message_id, 'msg': prev_msg}, f)
            prev_msg += "\n🔄 Memulai ulang bot..."
            message.edit_text(
                prev_msg,
                parse_mode='Markdown'
            )
            
            os.execl(sys.executable, sys.executable, *sys.argv)
            
        except Exception as e:
            if os.path.exists(RESTART_FILE):
                os.remove(RESTART_FILE)
            error_traceback = traceback.format_exc()
            error_message = (
                f"❌ Terjadi kesalahan saat pembaruan/restart:\n"
                f"Error type: `{type(e).__name__}`\n"
                f"Error message: `{str(e)}`\n"
                f"Traceback:\n```\n{error_traceback}```"
            )
            
            if len(error_message) > 4096:
                timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
                error_file = f"/tmp/bot_error_{timestamp}.txt"
                with open(error_file, 'w') as f:
                    f.write(error_message)
                
                short_message = (
                    f"❌ Terjadi kesalahan saat pembaruan/restart:\n"
                    f"Error type: `{type(e).__name__}`\n"
                    f"Error message: `{str(e)}`\n👇🏿 File Full Error 👇🏿"
                )
                update.message.reply_text(short_message, parse_mode='Markdown')
                with open(error_file, 'rb') as f:
                    update.message.reply_document(
                        document=f,
                        filename=f"error_{timestamp}.txt",
                        caption="📁 Log detail error"
                    )
            else:
                update.message.reply_text(error_message, parse_mode='Markdown')
            print("Error in restart_pull:")
            print(error_traceback)
        
    def set_timer(self,update,context):
        args = context.args
        if args[0].upper() == 'SHOLAT':
            try:
                kota = ' '.join(args[1:]).upper()                
                self.jadwal_sholat(update,context,kota)
            except:
                self.help(update,context)
        else:            
            try:        
                huruf = ''
                try:
                    angka   = re.match("([0-9]+)([a-zA-Z]+)",args[0]).group(1)
                    huruf   = re.match("([0-9]+)([a-zA-Z]+)",args[0]).group(2)
                except:
                    angka   = args[0]
                    satuan  = 1

                if huruf == 's' or huruf == 'd' or huruf == '':
                    satuan  = 1
                elif huruf == 'm':
                    satuan  = 60
                elif huruf == 'h' or huruf == 'j':
                    satuan  = 3600
                else:
                    update.message.reply_text(kamus("cmd_salah"))
                    return

                self.hitung(update,context,args,int(angka)*satuan)
            except (IndexError, ValueError):
                self.set_jam(update,context, args)

    def hitung(self,update,context,args,due):
        try:
            z       = self.t1.is_alive()
            
            chat_id = update.message.chat_id
            if due <= 0:
                update.message.reply_text(kamus("jadwal_lewat"))                
                return
            
            pesan = ' '.join(update.message.text.split(" ")[2:])
            # match = re.match(r'^[A-Za-z0-9 ?!\/&,.:@]*$', pesan )
            # if match :
            sekarang    = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()+datetime.timedelta(seconds = 0, hours=0))
            waktu       = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()+datetime.timedelta(seconds=due,hours=0))
            chat_id     = update.message["chat"]["id"]
            chat_type   = update.message["chat"]["type"]
            user_id     = update.message.from_user.id
            user_name   = update.message.from_user['first_name']
            
            sql         = "INSERT INTO daftar_timer (waktu, chat_id, chat_type, user_id, user_name, pesan, done, sholat, kota) VALUES (?,?,?,?,?,?,?,'','')"
            cur.execute(sql,(waktu, chat_id, chat_type, user_id, user_name, pesan, 0))
            db.commit()                
            update.message.reply_text(kamus("jadwal_set")%(sekarang, waktu))
            # else:
            #     update.message.reply_text('incorrect string')
        except Exception as e:
            update.message.reply_text('%s\n%s'%(kamus("mogok"),e))

    def agenda(self,update,context):
        try:
            z       = self.t1.is_alive()
            user_id = update.message.from_user.id
            chat_id = update.message["chat"]["id"]
            sql     = "SELECT waktu, pesan, sholat, kota FROM daftar_timer WHERE user_id = '%s' AND chat_id = '%s' AND done = 0"%(user_id, chat_id)
            bar, jum = eksekusi(sql)

            if jum == 0:
                update.message.reply_text(kamus("jadwal_kosong"))
            else:
                cek = []
                for i in range(jum):
                    waktu       = bar[i][0]                    
                    sekarang    = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()+datetime.timedelta(seconds = 0, hours=0))
                    if sekarang > waktu:
                        teks    = kamus("sholat_lewat")
                        done    = "UPDATE daftar_timer SET done = 1 WHERE waktu = '%s' and chat_id = '%s' AND user_id = '%s'"%(waktu,chat_id,user_id)
                        cur.execute(done)
                        db.commit()
                    else:
                        teks    = ""
                    cek.append("%s %s %s %s %s"%(waktu, bar[i][1],bar[i][2],bar[i][3], teks))                    
                cek.sort()
                agenda  = ''.join('%s \n'%cek[i] for i in range(len(cek)))
                update.message.reply_text(kamus("jadwal_list")%agenda)
        except Exception as e:
            update.message.reply_text('%s\n%s'%(kamus("mogok"),e))
    
    # def error(self,update,context):
    #     """Log Errors caused by Updates."""
    #     logger.warning('Update "%s" caused error "%s"', update, context.error)

    
    def timer(self):
        while True:           
            sekarang    = datetime.datetime.now()
            hari        = datetime.datetime.strftime(sekarang.date(),"%a") 
            waktu       = '{:%Y-%m-%d %H:%M:%S}'.format(sekarang+datetime.timedelta(seconds = 0, hours=0))
            sql         = "SELECT waktu, pesan, chat_id, user_name, sholat, kota, user_id FROM daftar_timer WHERE waktu = '%s'"%waktu
            sql_corona  = "SELECT waktu, area, chat_id, positif, sembuh, meninggal, waktu_berikutnya FROM kawalCoronaSub WHERE  langganan = 1"
            # self.timer_corona(Update, CallbackContext, sql = sql_corona, waktu = waktu, sekarang = sekarang)
            self.timer_sholat(Update, CallbackContext, sql = sql, hari = hari, waktu = waktu)
            
            waktuBackup = '{:%H:%M:%S}'.format(datetime.datetime.now())
            if (str(waktuBackup) == '18:00:00'):
                self.set_backup()
            
            time.sleep(1)            
            
    def timer_sholat(self,update:Update,context,sql, hari, waktu):
        bot         = Bot(token = Config.TOKEN)
        bar, jum = self.eksekusi(sql)
        if jum != 0:
            for i in range(jum):
                # barWaktu       = bar[i][0]
                barPesan       = bar[i][1]
                barChat_id     = bar[i][2]
                barUser_name   = bar[i][3]
                barSholat      = bar[i][4]
                barKota        = bar[i][5]
                barUser_id     = bar[i][6]
                if len(barSholat) > 1:
                    if barPesan== 'sholat':
                        kata = "\n\n%s"%kamus("sholat_footnote")
                    else:
                        kata = ""
                    if hari == "Sun":
                        sholat_waktu = barPesan
                        if sholat_waktu == "waktu":
                            sholat_waktu = "time"
                        else:
                            sholat_waktu = "prayer"
                        
                        if barSholat == "terbit":
                            sholat = "sunrise"
                        else:
                            sholat = barSholat
                        pesan = (kamus("sholat_teks")%(sholat,sholat_waktu, barKota, barUser_name,kata))
                    else:
                        pesan = (kamus("sholat_teks")%(barPesan, barSholat, barKota, barUser_name,kata))
                else:
                    if (barPesan.split()[0])=="banned":                                
                        try:
                            user_id = (barPesan.split()[1])
                            bot.send_sticker(barChat_id, 'CAADBQADSQ4AAs_rwQcgxkK2JzKWwhYE')  # banhammer marie sticker
                            bot.kick_chat_member(barChat_id, user_id)
                            pesan = ("banned [%s](tg://user?id=%s)"%(barUser_name,user_id))
                        except Exception as e:                            
                            pesan = ("ane gagal %s - [%s](tg://user?id=%s)"%(barPesan,barUser_name, barUser_id))
                            bot.send_sticker(barChat_id, 'CAACAgUAAxkBAAIVY18FFska2MmU5E4nPNco6m0RTRQhAALaAAM_5Bom20PZpUJeLM8aBA')  # banhammer marie sticker
                            done = "UPDATE new_members SET done = 1, age = '%s' WHERE chat_id = '%s' AND user_id = '%s'"%(0, barChat_id, barUser_id)
                            self.cur.execute(done)
                            self.db.commit()
                    else:
                        pesan = ("%s - [%s](tg://user?id=%s)"%(barPesan,barUser_name,barUser_id))
                
                try:
                    bot.send_message(text = pesan,chat_id = barChat_id,parse_mode=ParseMode.MARKDOWN)
                except:
                    bot.send_message(text = pesan,chat_id = barChat_id)
                done = "UPDATE daftar_timer SET done = 1 WHERE waktu = '%s' and chat_id = '%s'"%(waktu, barChat_id)
                self.cur.execute(done)
                self.db.commit()
                del barPesan, barUser_name, barSholat, barKota        

    def timer_corona(self,update,context,sql, waktu, sekarang):    
        bot         = Bot(token = Config.TOKEN)
        barCor,jumCor = eksekusi(sql)
        if jumCor != 0:            
            for i in range(jumCor):                
                cek_date = barCor[i][6]                        
                if cek_date > waktu:
                    pass
                elif cek_date < waktu:
                    # menghitung ulang saat waktu nya kelewat
                    berikutnya  = sekarang+datetime.timedelta(seconds = 300, hours=0)
                    berikutnya  = '{:%Y-%m-%d %H:%M:%S}'.format(berikutnya)    
                    chat_id     = barCor[i][2]
                    provinsi    = barCor[i][1]
                    sql_update  = "UPDATE kawalCoronaSub SET waktu_berikutnya=? WHERE chat_id = ? AND area = ? AND langganan = 1"
                    arg_update  = (berikutnya,chat_id,provinsi)
                    cur.execute(sql_update,arg_update)
                    db.commit()
                else:
                    try:                    
                        total_lama  = barCor[i][3]+barCor[i][4]+barCor[i][5]
                        chat_id     = barCor[i][2]
                        provinsi    = barCor[i][1]                                  
                        kode, tampil, positif, sembuh, meninggal  = kawalCorona.stat_corona(update,context,provinsi,chat_id)
                        pesan       = kawalCorona.corGraph(update,context,provinsi,chat_id)                                
                        total_baru  = int(positif)+int(sembuh)+int(meninggal)
                        if int(positif) - barCor[i][3]>0:
                            selisih_positif = "+%s"%(int(positif)-barCor[i][3])
                        else:
                            selisih_positif = "-%s"%(barCor[i][3]-int(positif))

                        if int(sembuh) - barCor[i][4]>0:
                            selisih_sembuh = "+%s"%(int(sembuh)-barCor[i][4])
                        else:
                            selisih_sembuh = "-%s"%(barCor[i][4]-int(sembuh))

                        if int(meninggal) - barCor[i][5]>0:
                            selisih_meninggal = "+%s"%(int(meninggal)-barCor[i][5])
                        else:
                            selisih_meninggal = "-%s"%(barCor[i][5]-int(meninggal))

                        tampil.append("``` Data sebelumnya %s\n Positif\t\t: %s\t\t%s\n Sembuh\t\t\t: %s\t\t%s\n Meninggal: %s\t\t%s```"%(barCor[i][0], barCor[i][3], selisih_positif,barCor[i][4],selisih_sembuh,barCor[i][5],selisih_meninggal))
                        if total_lama != total_baru:
                            tampil = (''.join('%s \n'%tampil[j] for j in range(len(tampil))))
                            if pesan:
                                filename= "%s%s"%(provinsi,chat_id)
                                file    = open("%s.png"%filename,"rb")
                                bot.sendPhoto(chat_id=chat_id, photo=file, caption=tampil, parse_mode = ParseMode.MARKDOWN)
                            else:
                                bot.send_message(text = tampil,chat_id = chat_id,parse_mode=ParseMode.MARKDOWN)
                            sekarang    = '{:%Y-%m-%d %H:%M:%S}'.format(sekarang)
                            sqlStat     = "INSERT INTO kawalCorona (tanggal, chat_id,area,positif,sembuh,meninggal) VALUES (?,?,?,?,?,?)"
                            argStat     = (sekarang,chat_id,provinsi, positif, sembuh, meninggal)
                            cur.execute(sqlStat, argStat)
                            db.commit()
                    except:
                        pass
                del cek_date

    def set_backup(self):
        bot         = Bot(token = Config.TOKEN)
        src = sqlite3.connect('database')
        dst = sqlite3.connect('backup.db')
        with dst:
            src.backup(dst, pages=1)
        dst.close()
        src.close()

        now     = datetime.datetime.now()
        tanggal = now.strftime("%d%m%Y-%H%M%S")
        namaFile= f"sarbot{tanggal}.tar.gz"
        tar     = tarfile.open(namaFile, "w:gz")
        chatId  = Config.BOT_CHAT_ID

        for root, dirs, files in os.walk(os.getcwd()):
            for name in files:
                if (name.endswith((".py",".py")) or name == 'database'):
                    tar.add(os.path.join(root, name))
        tar.close()


        file = open(namaFile,"rb")
        bot.send_document(chatId, file)

    def koneksiDatabase(self):
        self.db          = sqlite3.connect(pathDB, check_same_thread = False)
        self.cur         = db.cursor()

    def eksekusi(self, sql):
        self.cur.execute(sql)
        self.db.commit()
        lineData = self.cur.fetchall()
        totData  = len(lineData)
        return lineData, totData


if __name__ == '__main__':
    bot_timer()
