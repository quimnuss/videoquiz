import yaml
import gizeh as gz
import textwrap

# pyinstaller doesnt like exec() way of discovering packages of moviepy
# uncomment once moviepy fixes that
# import moviepy.editor as mpy

from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.VideoClip import ImageClip, VideoClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import AudioClip, CompositeAudioClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.fx.accel_decel import accel_decel
from moviepy.video.fx.blackwhite import blackwhite
from moviepy.video.fx.blink import blink
from moviepy.video.fx.colorx import colorx
from moviepy.video.fx.crop import crop
from moviepy.video.fx.even_size import even_size
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout
from moviepy.video.fx.freeze import freeze
from moviepy.video.fx.freeze_region import freeze_region
from moviepy.video.fx.gamma_corr import gamma_corr
from moviepy.video.fx.headblur import headblur
from moviepy.video.fx.invert_colors import invert_colors
from moviepy.video.fx.loop import loop
from moviepy.video.fx.lum_contrast import lum_contrast
from moviepy.video.fx.make_loopable import make_loopable
from moviepy.video.fx.margin import margin
from moviepy.video.fx.mask_and import mask_and
from moviepy.video.fx.mask_color import mask_color
from moviepy.video.fx.mask_or import mask_or
from moviepy.video.fx.mirror_x import mirror_x
from moviepy.video.fx.mirror_y import mirror_y
from moviepy.video.fx.painting import painting
from moviepy.video.fx.resize import resize
from moviepy.video.fx.rotate import rotate
from moviepy.video.fx.scroll import scroll
from moviepy.video.fx.speedx import speedx
from moviepy.video.fx.supersample import supersample
from moviepy.video.fx.time_mirror import time_mirror
from moviepy.video.fx.time_symmetrize import time_symmetrize

# from moviepy.audio.fx.audio_fadein import audio_fadein
from moviepy.audio.fx.audio_fadeout import audio_fadeout
from moviepy.audio.fx.audio_left_right import audio_left_right
from moviepy.audio.fx.audio_loop import audio_loop
from moviepy.audio.fx.audio_normalize import audio_normalize
from moviepy.audio.fx.volumex import volumex

# prod
# import warnings

# warnings.filterwarnings("ignore")

VIDEO_SIZE = (640, 480)
BLUE = (59 / 255, 89 / 255, 152 / 255)
GREEN = (176 / 255, 210 / 255, 63 / 255)
WHITE = (255, 255, 255)
WHITE_GIZEH = (1, 1, 1)
DURATION = 10


def countdown(t):
    surface = gz.Surface(100, 60, bg_color=WHITE_GIZEH)
    text = gz.text(
        f"0:{int(QUESTION_DURATION) - int(t):02}",
        fontfamily="Charter",
        fontsize=30,
        fontweight="bold",
        fill=BLUE,
        xy=(50, 30),
    )
    text.draw(surface)
    return surface.get_npimage()


def title_text(t, title):
    surface = gz.Surface(320, 100, bg_color=None)

    titles = textwrap.wrap(title, 28)

    for i, subtitle in enumerate(titles):
        text = gz.text(
            subtitle,
            fontfamily="Charter",
            fontsize=22,
            fontweight="bold",
            fill=BLUE,
            xy=(320 / 2, 15 + 50 / 2 + 25 * i),
        )
        text.draw(surface)
    return surface.get_npimage(transparent=True)


def transparent_textclip(text_gz_function, title, duration):
    graphics_clip_mask = VideoClip(
        lambda t: text_gz_function(t, title)[:, :, 3] / 255.0, duration=duration, ismask=True)
    graphics_clip = VideoClip(
        lambda t: text_gz_function(t, title)[:, :, :3],
        duration=duration).set_mask(graphics_clip_mask)
    # debugging sizes (displays background box)
    # graphics_clip = VideoClip(
    #     lambda t: text_gz_function(t)[:, :, :3], duration=QUESTION_DURATION)
    return graphics_clip


def add_question(timeline, cliplib, title, resposta, image_url):

    questiontl = []

    background_image = resize(ImageClip(image_url).set_position(("center", 0)), VIDEO_SIZE)

    text = transparent_textclip(title_text, title, QUESTION_DURATION)

    question_video = CompositeVideoClip(
        [
            background_image, cliplib['question_back'], cliplib['ct'].set_position(
                (VIDEO_SIZE[0] - cliplib['ct'].size[0], 0)),
            text.set_position((40, VIDEO_SIZE[1] - text.size[1] - 50))
        ],
        size=VIDEO_SIZE,
    ).set_duration(QUESTION_DURATION)

    timeline.append(question_video)
    questiontl.append(question_video)

    text = transparent_textclip(title_text, resposta, QUESTION_DURATION)

    response_video = CompositeVideoClip(
        [
            background_image, cliplib['question_back'],
            text.set_position((40, VIDEO_SIZE[1] - text.size[1] - 50))
        ],
        size=VIDEO_SIZE,
    ).set_duration(QUESTION_DURATION)

    timeline.append(response_video)
    questiontl.append(response_video)

    return questiontl


if __name__ == "__main__":

    with open('assets/preguntes.yaml') as file:
        question_list = yaml.load(file, Loader=yaml.SafeLoader)

    timeline = []

    cliplib = {}

    entradeta = resize(VideoFileClip("assets/entradeta.mp4"), VIDEO_SIZE)
    timeline.append(entradeta)
    entradeta.close()

    question_backclip = resize(VideoFileClip("assets/pregunta_background.mp4"), VIDEO_SIZE)
    cliplib['question_back'] = loop(mask_color(question_backclip, color=[0, 0, 0]), duration=10)

    global QUESTION_DURATION
    QUESTION_DURATION = cliplib['question_back'].duration

    cliplib['ct'] = VideoClip(countdown, duration=QUESTION_DURATION)

    for question in question_list:

        qtl = add_question(timeline, cliplib, question['title'], question['resposta'],
                           question['image_url'])

        # debug
        # qvideo = concatenate_videoclips(qtl)
        # qvideo.write_videofile(f"pregunta-{question['title]}.mp4", fps=10)

    qvideo = concatenate_videoclips(timeline)

    audioclip = AudioFileClip("assets/catquiz_audio.mp3")
    new_audioclip = CompositeAudioClip([audioclip]).set_duration(qvideo.duration)
    qvideo.audio = new_audioclip

    qvideo.write_videofile("catquiz.mp4", fps=10)
