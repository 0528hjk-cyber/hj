#!/usr/bin/env python3
"""Build the vlog from raw clips: cut segments, burn styled captions, normalize audio.

Usage: python3 build.py RAW_DIR WORK_DIR OUT.mp4
Edit SEGMENTS / captions below and rerun to change the cut.
"""
import os
import subprocess
import sys

RAW, WORK, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(WORK, exist_ok=True)

# (clip, start, end, options)
#   speed: <1 = slow motion (used on 120fps clips)
#   portrait: pad a vertical clip with a blurred fill
#   crop: (w_frac, h_frac, x_frac, y_frac) punch-in, e.g. to keep bystanders out of frame
#   vol: original audio gain
# caps: list of (style, text, rel_start, rel_end); rel_end None = segment end
SEGMENTS = [
    # --- opening: walk ---
    ("181449", 0.5, 4.5, dict(portrait=True), [
        ("Base", "오늘도 그냥 걷는 하루.....", 0, None),
        ("Pink", "산책 갑니데이", 1.2, None)]),
    ("181449", 20.0, 23.0, dict(portrait=True), [
        ("Base", "목적지 없음 · 계획 없음", 0, None)]),
    ("181644", 0.0, 3.5, dict(portrait=True), [
        ("Yellow", "오늘의 착장", 0, None),
        ("Base", "스트라이프 셔츠 + 회색 티 + 청바지", 0, None)]),
    ("181644", 12.5, 15.5, dict(portrait=True), [
        ("Base", "편한 게 최고야.....", 0, None)]),
    # --- dinner ---
    ("183530", 0.0, 5.5, dict(), [
        ("Serif", "6:35pm", 0.2, None),
        ("Base", "배고파서 일단 들어옴", 1.0, None)]),
    ("183530", 31.0, 33.5, dict(crop=(0.9, 0.62, 0.05, 0.0)), [
        ("Base", "메뉴 고민 3초 컷", 0, None)]),
    ("183530", 51.0, 55.0, dict(), [
        ("Yellow", "벽에 적힌 거 보니까", 0, None),
        ("Base", "오래된 집이라는 사실.. 믿음 간다", 0, None)]),
    ("183530", 60.0, 62.5, dict(), [
        ("Base", "밑반찬 세팅 완료", 0, None)]),
    ("183821", 0.5, 3.5, dict(speed=0.5), [
        ("Pink", "감자탕 비주얼 무엇", 0.4, None),
        ("Base", "감자가 통째로 들어있어요", 0, None)]),
    ("183821", 12.0, 13.6, dict(), [
        ("Base", "깍두기는 국룰", 0, None)]),
    ("183821", 17.0, 19.3, dict(), [
        ("Base", "공기밥까지 풀세트", 0, None)]),
    ("183942", 18.0, 23.0, dict(vol=0.6), [
        ("Base", "이제부터 말 없음", 0, None)]),
    ("183942", 40.0, 45.0, dict(vol=0.6), [
        ("Yellow", "국물 한 입 먹자마자", 0, None),
        ("Base", "하루 피로가 녹는 맛..", 0, None)]),
    ("183942", 95.0, 100.0, dict(vol=0.6), [
        ("Pink", "밥 말아버림", 0.5, None),
        ("Base", "감자탕은 밥 말아야 완성 ㄹㅇ", 0, None)]),
    # --- cafe ---
    ("191713", 1.0, 5.0, dict(crop=(0.8, 0.8, 0.0, 0.2)), [
        ("Serif", "7:17pm", 0.2, None),
        ("Base", "배부르니까 카페로 이동", 0.6, None)]),
    ("191713", 39.0, 46.0, dict(crop=(0.8, 0.8, 0.0, 0.2)), [
        ("Yellow", "카페 오면 제일 먼저 하는 일", 0, None),
        ("Base", "화장 고치기 (중요)", 0, None)]),
    ("191713", 60.0, 65.0, dict(crop=(0.8, 0.8, 0.0, 0.2)), [
        ("Base", "커피 마시면서 수다 타임 ^^", 0, None)]),
    # --- bookstore ---
    ("195425", 0.0, 3.0, dict(), [
        ("Serif", "7:54pm", 0.2, None),
        ("Base", "소화시킬 겸 서점 구경", 0.6, None)]),
    ("195425", 6.0, 10.0, dict(), [
        ("Base", "베스트셀러부터 일단 펼쳐봄", 0, None)]),
    ("195425", 17.5, 20.0, dict(), [
        ("Pink", "다크 심리학..?", 0.2, None)]),
    ("195425", 69.0, 73.0, dict(), [
        ("Yellow", "제목에 끌려서 결국", 0, None),
        ("Base", "집어 들고 서서 읽는 중", 0, None)]),
    ("195425", 90.0, 95.0, dict(), [
        ("Base", "생각보다 술술 읽혀서 당황.....", 0, None)]),
    # --- 알라딘 ---
    ("211722", 0.0, 3.5, dict(), [
        ("Serif", "9:17pm", 0.2, None),
        ("Base", "한 군데 더 들렀어요", 0.6, None)]),
    ("211722", 16.5, 19.5, dict(), [
        ("Serif", "Aladin", 0.0, None)]),
    ("211752", 2.0, 5.0, dict(speed=0.5), [
        ("Base", "책 표지 구경하는 거 은근 재밌음", 0, None)]),
    ("211752", 10.5, 13.5, dict(), [
        ("Base", "사고 싶은 건 많지만 오늘은 참기", 0, None)]),
    # --- shop + ending ---
    ("211951", 9.0, 15.0, dict(), [
        ("Yellow", "마지막 코스", 0, None),
        ("Base", "소품샵 구경하다가", 0, None)]),
    ("211951", 18.0, 24.0, dict(), [
        ("Hand", "오늘도 무사히 하루 끝", 0.8, None),
        ("Base", "오늘은 여기까지!", 0.8, None)]),
]

W, H, FPS = 1920, 1080, 30

ASS_HEADER = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Base,Pretendard SemiBold,54,&H00FFFFFF,&H00FFFFFF,&H00303030,&H80000000,0,0,0,0,100,100,0,0,1,1.6,2,2,60,60,78,1
Style: Yellow,Pretendard SemiBold,42,&H0063E6F5,&H0063E6F5,&H00303030,&H80000000,0,0,0,0,100,100,0,0,1,1.4,2,2,60,60,146,1
Style: Pink,NanumSquareRound ExtraBold,118,&H00B87BF2,&H00B87BF2,&H00FFFFFF,&H60000000,0,0,0,0,100,100,0,0,1,3,2,5,60,60,0,1
Style: Serif,EB Garamond 12,140,&H00B87BF2,&H00B87BF2,&H00FFFFFF,&H60000000,0,0,0,0,100,100,0,0,1,2.2,2,5,60,60,0,1
Style: Hand,NanumBarunpen Bold,120,&H00A25FFF,&H00A25FFF,&H00FFFFFF,&H50000000,1,0,0,0,100,100,0,0,1,4,2,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def ts(t):
    cs = int(round(t * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def run(cmd):
    subprocess.run(cmd, check=True)


def render_segment(i, clip, a, b, opt):
    out = os.path.join(WORK, f"seg{i:02d}.mp4")
    speed = opt.get("speed", 1.0)
    vol = opt.get("vol", 0.8)
    if opt.get("portrait"):
        vf = (f"split[bg][fg];[bg]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
              f"gblur=sigma=40,eq=brightness=-0.08[bgb];[fg]scale=-2:{H}[fgs];[bgb][fgs]overlay=(W-w)/2:0")
    elif "crop" in opt:
        cw, ch, cx, cy = opt["crop"]
        vf = f"crop=iw*{cw}:ih*{ch}:iw*{cx}:ih*{cy},scale={W}:{H}"
    else:
        vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    vf += f",setpts=PTS/{speed},fps={FPS},format=yuv420p,setsar=1"
    dur = (b - a) / speed
    af = (f"atempo={speed},volume={vol}," if speed != 1.0 else f"volume={vol},")
    af += f"afade=t=in:d=0.08,afade=t=out:st={max(dur - 0.08, 0):.3f}:d=0.08,aresample=48000"
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(a), "-t", str(b - a), "-i", os.path.join(RAW, clip + ".mp4"),
         "-filter_complex", f"[0:v]{vf}[v];[0:a]{af}[a]", "-map", "[v]", "-map", "[a]",
         "-t", f"{dur:.3f}", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
         "-c:a", "aac", "-b:a", "192k", "-ac", "2", out])
    return out, dur


def main():
    parts, events, t = [], [], 0.0
    for i, (clip, a, b, opt, caps) in enumerate(SEGMENTS):
        path, dur = render_segment(i, clip, a, b, opt)
        parts.append(path)
        for style, text, rs, re_ in caps:
            end = t + (dur if re_ is None else re_)
            events.append(f"Dialogue: 0,{ts(t + rs)},{ts(end)},{style},,0,0,0,,{text}")
        t += dur
        print(f"seg{i:02d} {clip} {dur:.1f}s (total {t:.1f}s)", flush=True)

    ass = os.path.join(WORK, "captions.ass")
    with open(ass, "w", encoding="utf-8") as f:
        f.write(ASS_HEADER + "\n".join(events) + "\n")
    lst = os.path.join(WORK, "list.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{p}'\n" for p in parts)
    joined = os.path.join(WORK, "joined.mp4")
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", joined])
    run(["ffmpeg", "-v", "error", "-y", "-i", joined, "-vf", f"ass={ass}",
         "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT])
    print("done", OUT, f"{t:.1f}s")


main()
