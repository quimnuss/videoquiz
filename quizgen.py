import yaml
import moviepy.editor as mpy
import gizeh as gz
from math import pi
import textwrap

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
    graphics_clip_mask = mpy.VideoClip(
        lambda t: text_gz_function(t, title)[:, :, 3] / 255.0, duration=duration, ismask=True)
    graphics_clip = mpy.VideoClip(
        lambda t: text_gz_function(t, title)[:, :, :3],
        duration=duration).set_mask(graphics_clip_mask)
    # debugging sizes (displays background box)
    # graphics_clip = mpy.VideoClip(
    #     lambda t: text_gz_function(t)[:, :, :3], duration=QUESTION_DURATION)
    return graphics_clip


def add_question(timeline, cliplib, title, resposta, image_url):

    questiontl = []

    background_image = mpy.ImageClip(image_url).set_position(("center", 0)).resize(VIDEO_SIZE)

    text = transparent_textclip(title_text, title, QUESTION_DURATION)

    question_video = mpy.CompositeVideoClip(
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

    response_video = mpy.CompositeVideoClip(
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

    entradeta = mpy.VideoFileClip("assets/entradeta.mp4").resize(VIDEO_SIZE)
    timeline.append(entradeta)
    entradeta.close()

    question_backclip = mpy.VideoFileClip("assets/pregunta_background.mp4").resize(VIDEO_SIZE)
    cliplib['question_back'] = mpy.vfx.mask_color(
        question_backclip, color=[0, 0, 0]).loop(duration=10)

    global QUESTION_DURATION
    QUESTION_DURATION = cliplib['question_back'].duration

    cliplib['ct'] = mpy.VideoClip(countdown, duration=QUESTION_DURATION)

    for question in question_list:

        qtl = add_question(timeline, cliplib, question['title'], question['resposta'],
                           question['image_url'])

        # debug
        # qvideo = mpy.concatenate_videoclips(qtl)
        # qvideo.write_videofile(f"pregunta-{question['title]}.mp4", fps=10)

    qvideo = mpy.concatenate_videoclips(timeline)

    audioclip = mpy.AudioFileClip("assets/catquiz_audio.mp3")
    new_audioclip = mpy.CompositeAudioClip([audioclip]).set_duration(qvideo.duration)
    qvideo.audio = new_audioclip

    qvideo.write_videofile("catquiz.mp4", fps=10)
