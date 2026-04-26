import os
import struct
import time
from multiprocessing import resource_tracker, shared_memory

import cv2
import numpy as np

SHM_NAME = "shm_ar_video"
SHM_HEADER_SIZE = 16
WINDOW_NAME = "AR Shared Memory Stream"
FPS_REPORT_INTERVAL = 1.0


def has_display():
    return bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))


def remove_shm_from_resource_tracker():
    try:
        resource_tracker.unregister("/" + SHM_NAME, "shared_memory")
    except Exception:
        pass


def wait_for_escape(show_window):
    if show_window and cv2.waitKey(1) == 27:
        raise KeyboardInterrupt


def main():
    print("Waiting for shared memory stream...", flush=True)
    show_window = has_display()
    if show_window:
        print("Display detected; window preview enabled.", flush=True)
    else:
        print("Headless environment detected; text-only mode enabled.", flush=True)

    while True:
        shm = None

        try:
            try:
                shm = shared_memory.SharedMemory(name=SHM_NAME)
                remove_shm_from_resource_tracker()
                print("Shared memory stream attached.", flush=True)
            except FileNotFoundError:
                time.sleep(1.0)
                continue

            last_fid = 0
            fps_count = 0
            fps_start = time.perf_counter()

            while True:
                try:
                    header = bytes(shm.buf[:SHM_HEADER_SIZE])
                    fid, width, height = struct.unpack("QII", header)

                    if fid == last_fid:
                        wait_for_escape(show_window)
                        time.sleep(0.002)
                        continue

                    if width <= 0 or height <= 0:
                        wait_for_escape(show_window)
                        time.sleep(0.002)
                        continue

                    frame_size = width * height * 3
                    frame_end = SHM_HEADER_SIZE + frame_size
                    if frame_end > len(shm.buf):
                        raise ValueError

                    frame_bytes = bytes(shm.buf[SHM_HEADER_SIZE:frame_end])

                    if bytes(shm.buf[:SHM_HEADER_SIZE]) != header:
                        continue

                    last_fid = fid
                    fps_count += 1
                    now = time.perf_counter()
                    elapsed = now - fps_start
                    if elapsed >= FPS_REPORT_INTERVAL:
                        fps = fps_count / elapsed
                        print(
                            f"[SHM] fps={fps:.2f} fid={fid} size={width}x{height}",
                            flush=True,
                        )
                        fps_count = 0
                        fps_start = now

                    if show_window:
                        frame_view = np.frombuffer(frame_bytes, dtype=np.uint8).reshape(
                            (height, width, 3)
                        )
                        frame = cv2.cvtColor(
                            cv2.flip(frame_view, 0), cv2.COLOR_RGB2BGR
                        )

                        cv2.imshow(WINDOW_NAME, frame)
                        wait_for_escape(show_window)
                except (BufferError, ValueError, struct.error):
                    raise FileNotFoundError
        except KeyboardInterrupt:
            break
        except FileNotFoundError:
            if shm is not None:
                shm.close()
            if show_window:
                cv2.destroyAllWindows()
            time.sleep(1.0)
        finally:
            if shm is not None:
                try:
                    shm.close()
                except Exception:
                    pass

    if show_window:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
