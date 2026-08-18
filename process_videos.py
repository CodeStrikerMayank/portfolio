import os
import subprocess
import shutil
import imageio_ffmpeg

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
os.makedirs('neural', exist_ok=True)
os.makedirs('Nerual Network', exist_ok=True)

# Configuration for trimming: (source_file, start_sec, duration_sec, base_name)
configs = [
    ('Nerual Network/neural_nexus.mp4', 2.0, 7.0, 'neural_nexus'),
    ('Nerual Network/simulationjet.mp4', 2.0, 6.0, 'simulationjet'),
    ('Nerual Network/simulationdrone.mp4', 3.0, 6.0, 'simulationdrone'),
    ('Nerual Network/trajectory.mp4', 0.0, 6.0, 'trajectory')
]

for src, start, dur, name in configs:
    print(f'Processing {name} from {src} (start: {start}s, dur: {dur}s)...')
    
    mp4_out = f'neural/{name}.mp4'
    webm_out = f'neural/{name}.webm'
    poster_out = f'neural/{name}_poster.jpg'
    
    # 1. Generate MP4 (H.264, even dimensions, 30fps, crf 24, faststart, no audio)
    cmd_mp4 = [
        ffmpeg, '-ss', str(start), '-t', str(dur), '-i', src,
        '-vf', "scale='min(1280,trunc(iw/2)*2)':-2,fps=30",
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '24',
        '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
        '-an', mp4_out, '-y'
    ]
    res_mp4 = subprocess.run(cmd_mp4, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    if res_mp4.returncode != 0:
        print(f'Error on {name} MP4: {res_mp4.stderr}')
        continue
    
    # 2. Generate WebM (VP9, even dimensions, 30fps, crf 30, no audio)
    cmd_webm = [
        ffmpeg, '-ss', str(start), '-t', str(dur), '-i', src,
        '-vf', "scale='min(1280,trunc(iw/2)*2)':-2,fps=30",
        '-c:v', 'libvpx-vp9', '-crf', '30', '-b:v', '0',
        '-pix_fmt', 'yuv420p',
        '-an', webm_out, '-y'
    ]
    res_webm = subprocess.run(cmd_webm, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    if res_webm.returncode != 0:
        print(f'Error on {name} WebM: {res_webm.stderr}')
        continue
    
    # 3. Generate Poster from first frame of trimmed mp4
    cmd_poster = [
        ffmpeg, '-ss', '0.1', '-i', mp4_out,
        '-vframes', '1', '-q:v', '2', poster_out, '-y'
    ]
    subprocess.run(cmd_poster, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Also sync to 'Nerual Network' folder for backwards compatibility
    legacy_mp4 = f'Nerual Network/{name}.mp4'
    legacy_poster = f'Nerual Network/{name}_poster.jpg'
    shutil.copyfile(mp4_out, legacy_mp4)
    shutil.copyfile(poster_out, legacy_poster)

    # Check sizes
    sz_mp4 = os.path.getsize(mp4_out) / 1024
    sz_webm = os.path.getsize(webm_out) / 1024
    sz_poster = os.path.getsize(poster_out) / 1024
    print(f'  [OK] {name}.mp4: {sz_mp4:.1f} KB | {name}.webm: {sz_webm:.1f} KB | poster: {sz_poster:.1f} KB')

# Also handle Simiulationdrone and special names in Nerual Network
shutil.copyfile('neural/simulationdrone.mp4', 'Nerual Network/Simiulationdrone.mp4')
shutil.copyfile('neural/trajectory.mp4', 'Nerual Network/trajecotry.mp4')
shutil.copyfile('neural/trajectory_poster.jpg', 'Nerual Network/trajecotry_poster.jpg')
shutil.copyfile('neural/neural_nexus.mp4', 'Nerual Network/Neural Nexus __ Knowledge Topology Dashboard (1).mp4')

print('\nProcessing showcase and hero videos for WebM...')
showcase_vids = [
    ('adr.mp4', 'adr.webm'),
    ('hello_1.mp4', 'hello_1.webm'),
    ('VID-20260405-WA0008.mp4', 'VID-20260405-WA0008.webm')
]

for src, out in showcase_vids:
    if os.path.exists(src):
        cmd = [
            ffmpeg, '-i', src,
            '-vf', "scale='min(1280,trunc(iw/2)*2)':-2,fps=30",
            '-c:v', 'libvpx-vp9', '-crf', '32', '-b:v', '0',
            '-pix_fmt', 'yuv420p',
            '-an', out, '-y'
        ]
        res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        if res.returncode == 0:
            sz = os.path.getsize(out) / 1024
            print(f'  [OK] {out}: {sz:.1f} KB')
        else:
            print(f'  Error on {out}: {res.stderr}')

print('\nALL VIDEOS PROCESSED AND OPTIMIZED SUCCESSFULLY!')

