# Kronos Kontrol — demo videos

| File | What |
|---|---|
| `KronosKontrol_1.0b_REAPER_demo.mp4` | silent screen capture, 2:20, 1500×404, 30 fps — the exported VST3 in REAPER 7.80 (rack, About, Editor tour) |
| `KronosKontrol_1.0b_REAPER_demo_music.mp4` | **the one to post** — same video with the JonasBlakewood track, loudness −14 LUFS target, 4 s fade-out at 2:16 |
| `KronosKontrol_1.0b_VST3_demo_1440p.mp4` | **YouTube upload** — same video upscaled to 2560×1440 (16:9, black bars), the capture's 12 px of REAPER window border on the right (grey scrollbar + resize grip) cropped and the blue FX-window badge top-left painted out, last frame held 4 s (2:24), music −14 LUFS with a 13 s fade-out (−60 dB, linear in dB) from 2:11 so it never cuts |
| `jonasblakewood-synthwave-618628.mp3` | music : "Synthwave" by JonasBlakewood, Pixabay (track id 618628), Pixabay Content License — free for this use, no credit required (credit appreciated) |
| `kk_soundtrack*.mp3`, `make_soundtrack*.py` | original alternatives synthesised for the video (not used) |

Mix command (ffmpeg 9.0.2, `C:\Users\Superdad\tools\ffmpeg`) :

```
ffmpeg -i KronosKontrol_1.0b_REAPER_demo.mp4 -i jonasblakewood-synthwave-618628.mp3 -filter_complex "[1:a]atrim=0:140,asetpts=PTS-STARTPTS,loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=out:st=136:d=4[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 -shortest -movflags +faststart KronosKontrol_1.0b_REAPER_demo_music.mp4
```

1440p YouTube version :

```
ffmpeg -i KronosKontrol_1.0b_REAPER_demo.mp4 -i jonasblakewood-synthwave-618628.mp3 -filter_complex "[0:v]crop=1488:404:0:0,drawbox=x=0:y=0:w=13:h=13:color=0x19181B:t=fill,drawbox=x=1472:y=390:w=16:h=14:color=0x201F22:t=fill,tpad=stop_mode=clone:stop_duration=4,scale=2560:694:flags=lanczos,pad=2560:1440:0:373:color=black,setsar=1,format=yuv420p[v];[1:a]atrim=0:144,asetpts=PTS-STARTPTS,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,volume=-1.1dB,volume='if(lt(t,131),1,pow(10,-3*(t-131)/13))':eval=frame[a]" -map "[v]" -map "[a]" -c:v libx264 -preset slow -crf 16 -r 30 -g 60 -bf 2 -c:a aac -b:a 320k -ar 48000 -t 144 -movflags +faststart KronosKontrol_1.0b_VST3_demo_1440p.mp4
```

Suggested credit line for the post : *Music: "Synthwave" by JonasBlakewood (Pixabay).*
