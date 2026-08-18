import os, re, struct

def verify():
    html_path = os.path.join(os.path.dirname(__file__), 'index.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Check all video sources
    video_srcs = re.findall(r'<source\s+src=["\']([^"\']+)["\']', html)
    print("=== Found video sources in HTML ===")
    all_ok = True
    for s in video_srcs:
        full_p = os.path.join(os.path.dirname(__file__), s)
        exists = os.path.exists(full_p)
        sz = os.path.getsize(full_p) if exists else 0
        status = "OK" if exists else "MISSING"
        if not exists:
            all_ok = False
        print(f"[{status}] {s} (Size: {sz/(1024*1024):.2f} MB)")

    # 2. Check all video posters
    posters = re.findall(r'poster=["\']([^"\']+)["\']', html)
    print("\n=== Found video posters in HTML ===")
    for p in posters:
        full_p = os.path.join(os.path.dirname(__file__), p)
        exists = os.path.exists(full_p)
        sz = os.path.getsize(full_p) if exists else 0
        status = "OK" if exists else "MISSING"
        if not exists:
            all_ok = False
        print(f"[{status}] {p} (Size: {sz/1024:.1f} KB)")

    # 3. Verify faststart on all mp4 files
    print("\n=== Verifying Faststart (moov atom before mdat atom) on MP4s ===")
    for s in set(video_srcs):
        full_p = os.path.join(os.path.dirname(__file__), s)
        if os.path.exists(full_p):
            with open(full_p, 'rb') as f:
                f.seek(0, 2)
                tot_sz = f.tell()
                f.seek(0)
                pos = 0
                atoms = []
                while pos < tot_sz:
                    f.seek(pos)
                    data = f.read(8)
                    if len(data) < 8: break
                    asz, atype = struct.unpack('>I4s', data)
                    atype = atype.decode('latin1', errors='replace')
                    if asz == 1:
                        asz = struct.unpack('>Q', f.read(8))[0]
                    elif asz == 0:
                        asz = tot_sz - pos
                    atoms.append((atype, pos, asz))
                    pos += asz
                    if asz <= 0: break
                moov = [a for a in atoms if a[0] == 'moov']
                mdat = [a for a in atoms if a[0] == 'mdat']
                is_fast = bool(moov and mdat and moov[0][1] < mdat[0][1])
                if not is_fast:
                    all_ok = False
                print(f"[FASTSTART={is_fast}] {s}")

    print("\nOVERALL VALIDATION STATUS:", "PASS (100% READY)" if all_ok else "FAIL")

if __name__ == '__main__':
    verify()
